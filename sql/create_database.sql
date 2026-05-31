-- 先删库再重建（解决表已存在的问题）
DROP DATABASE IF EXISTS renwei;
CREATE DATABASE renwei CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE renwei;

-- ============================================
-- 1. 用户系统
-- ============================================

CREATE TABLE `user` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '用户ID',
    `username` VARCHAR(32) NOT NULL COMMENT '用户名',
    `nickname` VARCHAR(64) DEFAULT NULL COMMENT '昵称',
    `avatar_url` VARCHAR(512) DEFAULT NULL COMMENT '头像URL',
    `bio` VARCHAR(256) DEFAULT NULL COMMENT '个人简介',
    `email` VARCHAR(128) DEFAULT NULL COMMENT '邮箱',
    `phone` VARCHAR(16) DEFAULT NULL COMMENT '手机号',
    `password_hash` VARCHAR(256) DEFAULT NULL COMMENT '密码哈希（Java后端预留）',
    `status` TINYINT NOT NULL DEFAULT 1 COMMENT '状态: 0-禁用 1-正常 2-未激活',
    `role` TINYINT NOT NULL DEFAULT 0 COMMENT '角色: 0-普通用户 1-创作者 2-管理员',
    `follow_count` INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '关注数',
    `follower_count` INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '粉丝数',
    `work_count` INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '作品数',
    `like_count` INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '获赞数',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `deleted_at` DATETIME DEFAULT NULL COMMENT '软删除时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_username` (`username`),
    UNIQUE KEY `uk_email` (`email`),
    UNIQUE KEY `uk_phone` (`phone`),
    KEY `idx_status` (`status`),
    KEY `idx_role` (`role`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

CREATE TABLE `user_follow` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `user_id` BIGINT UNSIGNED NOT NULL COMMENT '关注者ID',
    `target_id` BIGINT UNSIGNED NOT NULL COMMENT '被关注者ID',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_user_target` (`user_id`, `target_id`),
    KEY `idx_target` (`target_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='关注关系表';

-- ============================================
-- 2. 内容系统 - 作品（图片/视频）
-- ============================================

CREATE TABLE `work` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '作品ID',
    `user_id` BIGINT UNSIGNED NOT NULL COMMENT '作者ID',
    `title` VARCHAR(128) DEFAULT NULL COMMENT '标题',
    `description` VARCHAR(512) DEFAULT NULL COMMENT '描述/创作故事',
    `media_type` TINYINT NOT NULL DEFAULT 1 COMMENT '类型: 1-图片 2-视频',
    `media_url` VARCHAR(512) NOT NULL COMMENT '媒体URL',
    `thumbnail_url` VARCHAR(512) DEFAULT NULL COMMENT '缩略图URL',
    `aspect_ratio` VARCHAR(8) DEFAULT '1:1' COMMENT '画幅比例',
    `status` TINYINT NOT NULL DEFAULT 1 COMMENT '状态: 0-审核中 1-公开 2-私密 3-删除',
    `view_count` INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '浏览数',
    `like_count` INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '点赞数',
    `comment_count` INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '评论数',
    `collect_count` INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '收藏数',
    `share_count` INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '分享数',
    `is_ai_generated` TINYINT NOT NULL DEFAULT 1 COMMENT '是否AI生成: 0-否 1-是',
    `ai_model_id` VARCHAR(64) DEFAULT NULL COMMENT '生成模型ID（关联model_registry）',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `deleted_at` DATETIME DEFAULT NULL,
    PRIMARY KEY (`id`),
    KEY `idx_user_id` (`user_id`),
    KEY `idx_status` (`status`),
    KEY `idx_media_type` (`media_type`),
    KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='作品表';

CREATE TABLE `work_tag` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `work_id` BIGINT UNSIGNED NOT NULL,
    `tag_name` VARCHAR(32) NOT NULL COMMENT '标签名',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_work_tag` (`work_id`, `tag_name`),
    KEY `idx_tag` (`tag_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='作品标签表';

CREATE TABLE `work_like` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `work_id` BIGINT UNSIGNED NOT NULL,
    `user_id` BIGINT UNSIGNED NOT NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_work_user` (`work_id`, `user_id`),
    KEY `idx_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='点赞表';

CREATE TABLE `work_collect` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `work_id` BIGINT UNSIGNED NOT NULL,
    `user_id` BIGINT UNSIGNED NOT NULL,
    `folder_id` BIGINT UNSIGNED DEFAULT NULL COMMENT '收藏夹ID（预留）',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_work_user` (`work_id`, `user_id`),
    KEY `idx_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='收藏表';

CREATE TABLE `comment` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `work_id` BIGINT UNSIGNED NOT NULL,
    `user_id` BIGINT UNSIGNED NOT NULL,
    `parent_id` BIGINT UNSIGNED DEFAULT NULL COMMENT '父评论ID（楼中楼）',
    `content` VARCHAR(512) NOT NULL,
    `like_count` INT UNSIGNED NOT NULL DEFAULT 0,
    `status` TINYINT NOT NULL DEFAULT 1 COMMENT '0-删除 1-正常',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_work_id` (`work_id`),
    KEY `idx_parent_id` (`parent_id`),
    KEY `idx_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='评论表';

-- ============================================
-- 3. 创作系统 - AI生成记录（创作回放核心）
-- ============================================

CREATE TABLE `creation_session` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '创作会话ID',
    `user_id` BIGINT UNSIGNED NOT NULL,
    `session_key` VARCHAR(64) NOT NULL COMMENT '会话标识（对应Python session_id）',
    `status` TINYINT NOT NULL DEFAULT 1 COMMENT '状态: 0-结束 1-进行中',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_session_key` (`session_key`),
    KEY `idx_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='创作会话表';

CREATE TABLE `creation_record` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `session_id` BIGINT UNSIGNED NOT NULL COMMENT '关联creation_session.id',
    `user_id` BIGINT UNSIGNED NOT NULL,
    `user_input` VARCHAR(512) NOT NULL COMMENT '用户原始输入',
    `mode` VARCHAR(32) NOT NULL DEFAULT 'normal' COMMENT '模式: normal/incremental/clarification',
    `intent_json` JSON NOT NULL COMMENT 'IntentRepresentation完整JSON',
    `subject_entity` VARCHAR(128) DEFAULT NULL COMMENT '主体（冗余，方便查询）',
    `style_genre` VARCHAR(64) DEFAULT NULL COMMENT '风格（冗余）',
    `expert_outputs_json` JSON DEFAULT NULL COMMENT '各专家输出结果',
    `scheduled_experts` VARCHAR(128) DEFAULT NULL COMMENT '调度的专家列表',
    `final_prompt` TEXT NOT NULL COMMENT '最终提示词',
    `prompt_meta_json` JSON DEFAULT NULL COMMENT 'PromptEngineer元数据',
    `selected_model` VARCHAR(64) NOT NULL COMMENT '使用的模型',
    `image_url` VARCHAR(512) DEFAULT NULL COMMENT '生成图片URL',
    `video_url` VARCHAR(512) DEFAULT NULL COMMENT '生成视频URL（预留）',
    `generation_time_ms` INT UNSIGNED DEFAULT NULL COMMENT '生成耗时(ms)',
    `user_rating` TINYINT DEFAULT NULL COMMENT '用户评分 1-5',
    `user_feedback` VARCHAR(256) DEFAULT NULL COMMENT '用户反馈文字',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_session_id` (`session_id`),
    KEY `idx_user_id` (`user_id`),
    KEY `idx_style_genre` (`style_genre`),
    KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='创作记录表';

-- ============================================
-- 4. 模型调度台 - 众星云集核心
-- ============================================

CREATE TABLE `model_registry` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `model_key` VARCHAR(64) NOT NULL COMMENT '模型唯一标识',
    `model_name` VARCHAR(128) NOT NULL COMMENT '显示名称',
    `provider` VARCHAR(64) NOT NULL COMMENT '厂商: doubao/aliyun/openai/midjourney/...',
    `api_type` VARCHAR(32) NOT NULL DEFAULT 'openai' COMMENT 'API类型: openai/aliyun/volces/custom',
    `api_key_encrypted` VARCHAR(512) DEFAULT NULL COMMENT '加密后的API Key',
    `base_url` VARCHAR(256) DEFAULT NULL COMMENT 'API基础URL',
    `model_id` VARCHAR(128) NOT NULL COMMENT '模型ID（厂商侧标识）',
    `capabilities_json` JSON NOT NULL COMMENT '能力标签',
    `strengths_json` JSON DEFAULT NULL COMMENT '擅长领域',
    `params_json` JSON DEFAULT NULL COMMENT '模型参数',
    `prompt_template` TEXT DEFAULT NULL COMMENT '提示词模板',
    `is_active` TINYINT NOT NULL DEFAULT 1 COMMENT '0-禁用 1-启用',
    `is_verified` TINYINT NOT NULL DEFAULT 0 COMMENT '0-未验证 1-已验证',
    `verified_at` DATETIME DEFAULT NULL,
    `last_used_at` DATETIME DEFAULT NULL,
    `call_count` INT UNSIGNED NOT NULL DEFAULT 0,
    `error_count` INT UNSIGNED NOT NULL DEFAULT 0,
    `is_builtin` TINYINT NOT NULL DEFAULT 0 COMMENT '0-用户添加 1-系统内置',
    `user_id` BIGINT UNSIGNED DEFAULT NULL COMMENT '添加者ID',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_model_key` (`model_key`),
    KEY `idx_provider` (`provider`),
    KEY `idx_is_active` (`is_active`),
    KEY `idx_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='模型注册表';

CREATE TABLE `model_call_log` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `model_id` BIGINT UNSIGNED NOT NULL COMMENT '关联model_registry.id',
    `creation_record_id` BIGINT UNSIGNED DEFAULT NULL COMMENT '关联creation_record.id',
    `request_type` VARCHAR(32) NOT NULL COMMENT '请求类型: generate/validate/chat',
    `request_payload` JSON DEFAULT NULL COMMENT '请求参数',
    `response_payload` JSON DEFAULT NULL COMMENT '响应结果',
    `status` TINYINT NOT NULL DEFAULT 1 COMMENT '0-失败 1-成功',
    `error_msg` VARCHAR(512) DEFAULT NULL,
    `latency_ms` INT UNSIGNED DEFAULT NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_model_id` (`model_id`),
    KEY `idx_creation_record` (`creation_record_id`),
    KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='模型调用日志';

-- ============================================
-- 5. 社区系统
-- ============================================

CREATE TABLE `feed` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `user_id` BIGINT UNSIGNED NOT NULL COMMENT '发布者',
    `work_id` BIGINT UNSIGNED DEFAULT NULL COMMENT '关联作品',
    `content` VARCHAR(512) DEFAULT NULL COMMENT '动态文字内容',
    `media_urls_json` JSON DEFAULT NULL COMMENT '媒体URL数组',
    `like_count` INT UNSIGNED NOT NULL DEFAULT 0,
    `comment_count` INT UNSIGNED NOT NULL DEFAULT 0,
    `share_count` INT UNSIGNED NOT NULL DEFAULT 0,
    `status` TINYINT NOT NULL DEFAULT 1,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_user_id` (`user_id`),
    KEY `idx_work_id` (`work_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='动态/feed表';

CREATE TABLE `notification` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `user_id` BIGINT UNSIGNED NOT NULL COMMENT '接收者',
    `sender_id` BIGINT UNSIGNED DEFAULT NULL COMMENT '发送者',
    `type` TINYINT NOT NULL COMMENT '类型: 1-点赞 2-评论 3-关注 4-系统通知',
    `target_type` VARCHAR(32) DEFAULT NULL COMMENT '对象类型: work/comment/user',
    `target_id` BIGINT UNSIGNED DEFAULT NULL COMMENT '对象ID',
    `content` VARCHAR(256) DEFAULT NULL,
    `is_read` TINYINT NOT NULL DEFAULT 0,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_user_id` (`user_id`),
    KEY `idx_is_read` (`is_read`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='通知表';

CREATE TABLE `report` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `reporter_id` BIGINT UNSIGNED NOT NULL,
    `target_type` VARCHAR(32) NOT NULL COMMENT 'work/comment/user',
    `target_id` BIGINT UNSIGNED NOT NULL,
    `reason` VARCHAR(128) NOT NULL,
    `detail` VARCHAR(512) DEFAULT NULL,
    `status` TINYINT NOT NULL DEFAULT 0 COMMENT '0-待处理 1-已处理 2-驳回',
    `handled_by` BIGINT UNSIGNED DEFAULT NULL,
    `handled_at` DATETIME DEFAULT NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_target` (`target_type`, `target_id`),
    KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='举报表';

-- ============================================
-- 6. 风格库RAG（预留）
-- ============================================

CREATE TABLE `style_dna` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `user_id` BIGINT UNSIGNED NOT NULL COMMENT '创建者',
    `name` VARCHAR(64) NOT NULL COMMENT '风格名称',
    `description` VARCHAR(256) DEFAULT NULL,
    `reference_image_url` VARCHAR(512) DEFAULT NULL COMMENT '参考图',
    `style_features_json` JSON NOT NULL COMMENT '风格特征向量/参数',
    `prompt_template` TEXT DEFAULT NULL COMMENT '关联提示词模板',
    `is_public` TINYINT NOT NULL DEFAULT 0 COMMENT '0-私有 1-公开',
    `use_count` INT UNSIGNED NOT NULL DEFAULT 0,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_user_id` (`user_id`),
    KEY `idx_is_public` (`is_public`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='风格DNA库';

-- ============================================
-- 7. 提示词审查日志（预留）
-- ============================================

CREATE TABLE `prompt_audit` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `creation_record_id` BIGINT UNSIGNED NOT NULL,
    `original_prompt` TEXT NOT NULL,
    `processed_prompt` TEXT NOT NULL,
    `audit_result` TINYINT NOT NULL DEFAULT 1 COMMENT '0-拦截 1-通过 2-警告',
    `risk_score` INT DEFAULT NULL COMMENT '风险评分 0-100',
    `risk_type` VARCHAR(32) DEFAULT NULL COMMENT '风险类型',
    `blocked_keywords` JSON DEFAULT NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_creation_record` (`creation_record_id`),
    KEY `idx_audit_result` (`audit_result`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='提示词审查日志';

-- ============================================
-- 初始化数据
-- ============================================

INSERT INTO `model_registry` (
    `model_key`, `model_name`, `provider`, `api_type`, `model_id`,
    `capabilities_json`, `strengths_json`, `params_json`, `is_builtin`, `is_active`, `is_verified`
) VALUES (
    'seedream',
    'Doubao Seedream-5.0',
    'doubao',
    'openai',
    'doubao-seedream-5-0-260128',
    '["photo_realistic", "high_detail", "chinese_prompt", "fast", "image"]',
    '["portrait", "landscape", "anime", "concept"]',
    '{"max_tokens": 4096, "temperature": 0.7}',
    1, 1, 1
);

INSERT INTO `model_registry` (
    `model_key`, `model_name`, `provider`, `api_type`, `model_id`,
    `capabilities_json`, `strengths_json`, `is_builtin`, `is_active`, `is_verified`
) VALUES (
    'deepseek-v4-pro',
    'DeepSeek-v4-pro',
    'deepseek',
    'openai',
    'deepseek-v4-pro',
    '["reasoning", "json_output", "fast", "chat"]',
    '["scheduling", "fusion", "analysis"]',
    1, 1, 1
);

INSERT INTO `model_registry` (
    `model_key`, `model_name`, `provider`, `api_type`, `model_id`,
    `capabilities_json`, `strengths_json`, `is_builtin`, `is_active`, `is_verified`
) VALUES (
    'qwen3.6-plus',
    'Qwen3.6-plus',
    'aliyun',
    'aliyun',
    'qwen3.6-plus',
    '["vision", "long_context", "chinese", "chat"]',
    '["image_analysis", "ocr", "video_understanding"]',
    1, 1, 1
);

INSERT INTO `model_registry` (
    `model_key`, `model_name`, `provider`, `api_type`, `model_id`,
    `capabilities_json`, `strengths_json`, `is_builtin`, `is_active`
) VALUES (
    'wanxiang',
    'Wanxiang',
    'aliyun',
    'aliyun',
    'wanx-v1',
    '["image", "chinese_prompt", "style_transfer"]',
    '["chinese_art", "ink_wash", "traditional"]',
    1, 0
);

INSERT INTO `model_registry` (
    `model_key`, `model_name`, `provider`, `api_type`, `model_id`,
    `capabilities_json`, `strengths_json`, `is_builtin`, `is_active`
) VALUES (
    'keling',
    'Keling',
    'kuaishou',
    'custom',
    'kling-v1',
    '["video", "chinese_prompt", "motion"]',
    '["video_generation", "motion_control"]',
    1, 0
);