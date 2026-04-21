-- init_data.sql
-- 图书管理系统演示数据
-- 前置条件: 已执行 init_db.sql 和 manage.py migrate
-- 用法: mysql -uroot -p123456 library < init_data.sql
--
-- 演示账号（密码均为 Demo@123456）:
--   demo_admin     — 超级管理员
--   demo_librarian — 图书管理员
--   demo_reader    — 普通读者

USE `library`;
SET NAMES utf8mb4;
SET @now = NOW();

-- ============================================================
-- 1. 用户 (auth_user)
-- ============================================================
INSERT INTO `auth_user`
  (`id`,`password`,`last_login`,`is_superuser`,`username`,`first_name`,`last_name`,`email`,`is_staff`,`is_active`,`date_joined`)
VALUES
  (1, 'pbkdf2_sha256$600000$n5zPEJ6sEZSxQ0SPcoUD9g$O9PmdX90Kx6u3MFqkThVae+cGVSXwNJDSpWWrG1unds=',
      @now, 1, 'demo_admin',     '管理员', '张', 'admin@library.local',     1, 1, @now),
  (2, 'pbkdf2_sha256$600000$n5zPEJ6sEZSxQ0SPcoUD9g$O9PmdX90Kx6u3MFqkThVae+cGVSXwNJDSpWWrG1unds=',
      @now, 0, 'demo_librarian', '馆员',   '李', 'librarian@library.local', 1, 1, @now),
  (3, 'pbkdf2_sha256$600000$n5zPEJ6sEZSxQ0SPcoUD9g$O9PmdX90Kx6u3MFqkThVae+cGVSXwNJDSpWWrG1unds=',
      @now, 0, 'demo_reader',    '读者',   '王', 'reader@library.local',    0, 1, @now);

-- ============================================================
-- 2. 用户资料 (book_profile)
-- ============================================================
INSERT INTO `book_profile` (`id`,`bio`,`phone_number`,`email`,`user_id`,`profile_pic`)
VALUES
  (1, '系统管理员，负责整体运维',   '13800000001', 'admin@library.local',     1, ''),
  (2, '图书管理员，负责图书借还管理', '13800000002', 'librarian@library.local', 2, ''),
  (3, '热爱阅读的读者',             '13800000003', 'reader@library.local',    3, '');

-- ============================================================
-- 3. 权限组 (auth_group) + 用户-组关联
-- ============================================================
INSERT INTO `auth_group` (`id`,`name`) VALUES
  (1, 'logs'),
  (2, 'api'),
  (3, 'download_data');

INSERT INTO `auth_user_groups` (`user_id`,`group_id`) VALUES
  (1, 1), (1, 2), (1, 3),   -- admin 拥有全部权限组
  (2, 1), (2, 2);            -- librarian 拥有 logs + api

-- ============================================================
-- 4. 分类 (book_category)
-- ============================================================
INSERT INTO `book_category` (`id`,`name`,`created_at`) VALUES
  (1, '文学',     @now),
  (2, '计算机',   @now),
  (3, '历史',     @now),
  (4, '哲学',     @now),
  (5, '经济学',   @now),
  (6, '自然科学', @now),
  (7, '艺术',     @now),
  (8, '教育',     @now);

-- ============================================================
-- 5. 出版社 (book_publisher)
-- ============================================================
INSERT INTO `book_publisher` (`id`,`name`,`city`,`contact`,`created_at`,`updated_by`,`updated_at`) VALUES
  (1, '人民文学出版社',       '北京', 'contact@rwcbs.com',    @now, 'system', @now),
  (2, '机械工业出版社',       '北京', 'contact@cmpbook.com',  @now, 'system', @now),
  (3, '清华大学出版社',       '北京', 'contact@tup.com',      @now, 'system', @now),
  (4, '商务印书馆',           '北京', 'contact@cp.com',       @now, 'system', @now),
  (5, '电子工业出版社',       '北京', 'contact@phei.com',     @now, 'system', @now);

-- ============================================================
-- 6. 图书 (book_book)
-- ============================================================
INSERT INTO `book_book`
  (`id`,`author`,`title`,`description`,`created_at`,`updated_at`,
   `total_borrow_times`,`quantity`,`category_id`,`publisher_id`,
   `status`,`floor_number`,`bookshelf_number`,`updated_by`)
VALUES
  (1,  '鲁迅',       '呐喊',
       '中国现代文学经典短篇小说集，收录《狂人日记》《阿Q正传》等名篇。',
       @now, @now, 25, 12, 1, 1, 1, 1, 'A001', 'system'),
  (2,  '曹雪芹',     '红楼梦',
       '中国古典四大名著之一，以贾宝玉与林黛玉的爱情悲剧为主线。',
       @now, @now, 32, 8, 1, 1, 1, 1, 'A002', 'system'),
  (3,  '余华',       '活着',
       '讲述福贵一生的坎坷经历，展现了人对苦难的承受能力。',
       @now, @now, 28, 10, 1, 1, 1, 1, 'A003', 'system'),
  (4,  '刘慈欣',     '三体',
       '中国科幻里程碑作品，讲述地球文明与三体文明的首次接触。',
       @now, @now, 45, 15, 6, 5, 1, 2, 'B001', 'system'),
  (5,  '谭浩强',     'C程序设计',
       '经典C语言入门教材，被众多高校选为计算机专业基础课程教材。',
       @now, @now, 18, 20, 2, 3, 1, 2, 'B002', 'system'),
  (6,  'Thomas H. Cormen', '算法导论',
       '计算机科学经典教材，全面介绍算法设计与分析的基本方法。',
       @now, @now, 22, 6, 2, 2, 1, 2, 'B003', 'system'),
  (7,  '司马迁',     '史记',
       '中国第一部纪传体通史，被誉为"史家之绝唱，无韵之离骚"。',
       @now, @now, 15, 5, 3, 4, 1, 1, 'A004', 'system'),
  (8,  '冯友兰',     '中国哲学简史',
       '中国哲学入门经典，系统介绍从先秦到近代的哲学思想。',
       @now, @now, 12, 7, 4, 4, 1, 3, 'C001', 'system'),
  (9,  '曼昆',       '经济学原理',
       '全球畅销的经济学入门教材，以通俗易懂的方式讲解经济学基本原理。',
       @now, @now, 20, 9, 5, 2, 1, 3, 'C002', 'system'),
  (10, '霍金',       '时间简史',
       '探索宇宙本质的科普经典，从大爆炸到黑洞的物理学之旅。',
       @now, @now, 30, 11, 6, 5, 1, 2, 'B004', 'system'),
  (11, '贡布里希',   '艺术的故事',
       '西方艺术史入门经典，以生动的叙述带领读者了解艺术发展脉络。',
       @now, @now, 8, 4, 7, 4, 1, 3, 'C003', 'system'),
  (12, '陶行知',     '陶行知教育文集',
       '中国现代教育家陶行知的重要教育思想著作，倡导生活教育理论。',
       @now, @now, 6, 5, 8, 1, 1, 3, 'C004', 'system'),
  (13, '路遥',       '平凡的世界',
       '全景式反映中国当代城乡社会生活的长篇小说，获茅盾文学奖。',
       @now, @now, 35, 10, 1, 1, 1, 1, 'A005', 'system'),
  (14, '林奕含',     '房思琪的初恋乐园',
       '一部令人震撼的小说，关注青少年成长与社会问题。',
       @now, @now, 14, 6, 1, 1, 1, 1, 'A006', 'system'),
  (15, '吴军',       '数学之美',
       '将数学原理与信息技术相结合，揭示搜索引擎、自然语言处理等背后的数学之美。',
       @now, @now, 19, 8, 2, 5, 1, 2, 'B005', 'system');

-- ============================================================
-- 7. 会员 (book_member)
-- ============================================================
INSERT INTO `book_member`
  (`id`,`user_id`,`name`,`age`,`gender`,`city`,`email`,`phone_number`,
   `created_at`,`created_by`,`updated_by`,`updated_at`,
   `card_id`,`card_number`,`expired_at`)
VALUES
  (1, 3,    '王小明', 22, 'm', '北京', 'reader@library.local',    '13800000003',
     @now, 'demo_admin', 'demo_admin', @now,
     '11111111111111111111111111111111', '11111111', DATE_ADD(@now, INTERVAL 1 YEAR)),
  (2, NULL, '赵丽华', 25, 'f', '上海', 'zhao@example.com',        '13900000001',
     @now, 'demo_admin', 'demo_admin', @now,
     '22222222222222222222222222222222', '22222222', DATE_ADD(@now, INTERVAL 1 YEAR)),
  (3, NULL, '陈志远', 30, 'm', '广州', 'chen@example.com',        '13900000002',
     @now, 'demo_admin', 'demo_admin', @now,
     '33333333333333333333333333333333', '33333333', DATE_ADD(@now, INTERVAL 1 YEAR)),
  (4, NULL, '林小燕', 21, 'f', '深圳', 'lin@example.com',         '13900000003',
     @now, 'demo_admin', 'demo_admin', @now,
     '44444444444444444444444444444444', '44444444', DATE_ADD(@now, INTERVAL 1 YEAR)),
  (5, NULL, '张伟',   28, 'm', '杭州', 'zhangwei@example.com',    '13900000004',
     @now, 'demo_admin', 'demo_admin', @now,
     '55555555555555555555555555555555', '55555555', DATE_ADD(@now, INTERVAL 1 YEAR)),
  (6, NULL, '周杰',   24, 'm', '南京', 'zhoujie@example.com',     '13900000005',
     @now, 'demo_admin', 'demo_admin', @now,
     '66666666666666666666666666666666', '66666666', DATE_ADD(@now, INTERVAL 1 YEAR)),
  (7, NULL, '刘芳',   26, 'f', '成都', 'liufang@example.com',     '13900000006',
     @now, 'demo_admin', 'demo_admin', @now,
     '77777777777777777777777777777777', '77777777', DATE_ADD(@now, INTERVAL 1 YEAR)),
  (8, NULL, '黄磊',   32, 'm', '武汉', 'huanglei@example.com',    '13900000007',
     @now, 'demo_admin', 'demo_admin', @now,
     '88888888888888888888888888888888', '88888888', DATE_ADD(@now, INTERVAL 1 YEAR));

-- ============================================================
-- 8. 借阅记录 (book_borrowrecord)
-- ============================================================
INSERT INTO `book_borrowrecord`
  (`id`,`user_id`,`borrower`,`borrower_card`,`borrower_email`,`borrower_phone_number`,
   `book`,`book_link_id`,`book_title`,`quantity`,
   `start_day`,`end_day`,`periode`,
   `open_or_close`,`delay_days`,`final_status`,
   `created_at`,`created_by`,`closed_by`,`closed_at`)
VALUES
  -- 已归还的记录
  (1, 3, '王小明', '11111111', 'reader@library.local', '13800000003',
     '三体', 4, '三体', 1,
     DATE_SUB(@now, INTERVAL 30 DAY), DATE_SUB(@now, INTERVAL 23 DAY), 7,
     1, 0, 'On time',
     DATE_SUB(@now, INTERVAL 30 DAY), 'demo_admin', 'demo_admin', DATE_SUB(@now, INTERVAL 24 DAY)),

  (2, 3, '王小明', '11111111', 'reader@library.local', '13800000003',
     '呐喊', 1, '呐喊', 1,
     DATE_SUB(@now, INTERVAL 25 DAY), DATE_SUB(@now, INTERVAL 18 DAY), 7,
     1, 0, 'On time',
     DATE_SUB(@now, INTERVAL 25 DAY), 'demo_admin', 'demo_admin', DATE_SUB(@now, INTERVAL 19 DAY)),

  (3, NULL, '赵丽华', '22222222', 'zhao@example.com', '13900000001',
     '红楼梦', 2, '红楼梦', 1,
     DATE_SUB(@now, INTERVAL 20 DAY), DATE_SUB(@now, INTERVAL 13 DAY), 7,
     1, 0, 'On time',
     DATE_SUB(@now, INTERVAL 20 DAY), 'demo_librarian', 'demo_librarian', DATE_SUB(@now, INTERVAL 14 DAY)),

  (4, NULL, '陈志远', '33333333', 'chen@example.com', '13900000002',
     '经济学原理', 9, '经济学原理', 1,
     DATE_SUB(@now, INTERVAL 18 DAY), DATE_SUB(@now, INTERVAL 11 DAY), 7,
     1, 2, 'Delayed',
     DATE_SUB(@now, INTERVAL 18 DAY), 'demo_librarian', 'demo_librarian', DATE_SUB(@now, INTERVAL 9 DAY)),

  (5, NULL, '林小燕', '44444444', 'lin@example.com', '13900000003',
     '活着', 3, '活着', 1,
     DATE_SUB(@now, INTERVAL 15 DAY), DATE_SUB(@now, INTERVAL 8 DAY), 7,
     1, 0, 'On time',
     DATE_SUB(@now, INTERVAL 15 DAY), 'demo_admin', 'demo_admin', DATE_SUB(@now, INTERVAL 9 DAY)),

  (6, NULL, '张伟', '55555555', 'zhangwei@example.com', '13900000004',
     '算法导论', 6, '算法导论', 1,
     DATE_SUB(@now, INTERVAL 14 DAY), DATE_SUB(@now, INTERVAL 7 DAY), 7,
     1, 0, 'On time',
     DATE_SUB(@now, INTERVAL 14 DAY), 'demo_admin', 'demo_admin', DATE_SUB(@now, INTERVAL 8 DAY)),

  -- 正在借阅的记录 (open)
  (7, 3, '王小明', '11111111', 'reader@library.local', '13800000003',
     '平凡的世界', 13, '平凡的世界', 1,
     DATE_SUB(@now, INTERVAL 3 DAY), DATE_ADD(@now, INTERVAL 4 DAY), 7,
     0, 0, 'Unknown',
     DATE_SUB(@now, INTERVAL 3 DAY), 'demo_librarian', '', @now),

  (8, NULL, '赵丽华', '22222222', 'zhao@example.com', '13900000001',
     '时间简史', 10, '时间简史', 1,
     DATE_SUB(@now, INTERVAL 5 DAY), DATE_ADD(@now, INTERVAL 2 DAY), 7,
     0, 0, 'Unknown',
     DATE_SUB(@now, INTERVAL 5 DAY), 'demo_admin', '', @now),

  (9, NULL, '陈志远', '33333333', 'chen@example.com', '13900000002',
     '数学之美', 15, '数学之美', 1,
     DATE_SUB(@now, INTERVAL 2 DAY), DATE_ADD(@now, INTERVAL 5 DAY), 7,
     0, 0, 'Unknown',
     DATE_SUB(@now, INTERVAL 2 DAY), 'demo_librarian', '', @now),

  (10, NULL, '林小燕', '44444444', 'lin@example.com', '13900000003',
      '中国哲学简史', 8, '中国哲学简史', 1,
      DATE_SUB(@now, INTERVAL 1 DAY), DATE_ADD(@now, INTERVAL 6 DAY), 7,
      0, 0, 'Unknown',
      DATE_SUB(@now, INTERVAL 1 DAY), 'demo_admin', '', @now),

  -- 更多已归还记录
  (11, NULL, '赵丽华', '22222222', 'zhao@example.com', '13900000001',
      '艺术的故事', 11, '艺术的故事', 1,
      DATE_SUB(@now, INTERVAL 40 DAY), DATE_SUB(@now, INTERVAL 33 DAY), 7,
      1, 0, 'On time',
      DATE_SUB(@now, INTERVAL 40 DAY), 'demo_admin', 'demo_admin', DATE_SUB(@now, INTERVAL 34 DAY)),

  (12, NULL, '张伟', '55555555', 'zhangwei@example.com', '13900000004',
      'C程序设计', 5, 'C程序设计', 1,
      DATE_SUB(@now, INTERVAL 35 DAY), DATE_SUB(@now, INTERVAL 28 DAY), 7,
      1, 3, 'Delayed',
      DATE_SUB(@now, INTERVAL 35 DAY), 'demo_librarian', 'demo_librarian', DATE_SUB(@now, INTERVAL 25 DAY)),

  (13, NULL, '周杰', '66666666', 'zhoujie@example.com', '13900000005',
      '三体', 4, '三体', 1,
      DATE_SUB(@now, INTERVAL 12 DAY), DATE_SUB(@now, INTERVAL 5 DAY), 7,
      1, 0, 'On time',
      DATE_SUB(@now, INTERVAL 12 DAY), 'demo_admin', 'demo_admin', DATE_SUB(@now, INTERVAL 6 DAY)),

  (14, NULL, '刘芳', '77777777', 'liufang@example.com', '13900000006',
      '红楼梦', 2, '红楼梦', 1,
      DATE_SUB(@now, INTERVAL 10 DAY), DATE_SUB(@now, INTERVAL 3 DAY), 7,
      1, 0, 'On time',
      DATE_SUB(@now, INTERVAL 10 DAY), 'demo_librarian', 'demo_librarian', DATE_SUB(@now, INTERVAL 4 DAY)),

  (15, NULL, '黄磊', '88888888', 'huanglei@example.com', '13900000007',
      '史记', 7, '史记', 1,
      DATE_SUB(@now, INTERVAL 22 DAY), DATE_SUB(@now, INTERVAL 15 DAY), 7,
      1, 5, 'Delayed',
      DATE_SUB(@now, INTERVAL 22 DAY), 'demo_admin', 'demo_admin', DATE_SUB(@now, INTERVAL 10 DAY)),

  -- 新增正在借阅记录
  (16, NULL, '周杰', '66666666', 'zhoujie@example.com', '13900000005',
      '经济学原理', 9, '经济学原理', 1,
      DATE_SUB(@now, INTERVAL 4 DAY), DATE_ADD(@now, INTERVAL 3 DAY), 7,
      0, 0, 'Unknown',
      DATE_SUB(@now, INTERVAL 4 DAY), 'demo_librarian', '', @now),

  (17, NULL, '刘芳', '77777777', 'liufang@example.com', '13900000006',
      '陶行知教育文集', 12, '陶行知教育文集', 1,
      DATE_SUB(@now, INTERVAL 2 DAY), DATE_ADD(@now, INTERVAL 5 DAY), 7,
      0, 0, 'Unknown',
      DATE_SUB(@now, INTERVAL 2 DAY), 'demo_admin', '', @now),

  (18, NULL, '黄磊', '88888888', 'huanglei@example.com', '13900000007',
      '呐喊', 1, '呐喊', 1,
      DATE_SUB(@now, INTERVAL 6 DAY), DATE_ADD(@now, INTERVAL 1 DAY), 7,
      0, 0, 'Unknown',
      DATE_SUB(@now, INTERVAL 6 DAY), 'demo_librarian', '', @now);

-- ============================================================
-- 9. 用户操作记录 (book_useractivity)
-- ============================================================
INSERT INTO `book_useractivity` (`id`,`created_by`,`created_at`,`operation_type`,`target_model`,`detail`) VALUES
  (1, 'demo_admin',     DATE_SUB(@now, INTERVAL 30 DAY), 'success', 'Book',         '新增图书《三体》'),
  (2, 'demo_admin',     DATE_SUB(@now, INTERVAL 30 DAY), 'success', 'BorrowRecord', '创建借阅记录 王小明→三体'),
  (3, 'demo_admin',     DATE_SUB(@now, INTERVAL 24 DAY), 'info',    'BorrowRecord', '关闭借阅记录 王小明→三体'),
  (4, 'demo_librarian', DATE_SUB(@now, INTERVAL 20 DAY), 'success', 'BorrowRecord', '创建借阅记录 赵丽华→红楼梦'),
  (5,  'demo_admin',     DATE_SUB(@now, INTERVAL 5 DAY),  'warning', 'Book',         '更新图书《时间简史》库存'),
  (6,  'demo_admin',     DATE_SUB(@now, INTERVAL 28 DAY), 'success', 'Member',       '新增会员 赵丽华'),
  (7,  'demo_admin',     DATE_SUB(@now, INTERVAL 28 DAY), 'success', 'Member',       '新增会员 陈志远'),
  (8,  'demo_librarian', DATE_SUB(@now, INTERVAL 15 DAY), 'success', 'BorrowRecord', '创建借阅记录 林小燕→活着'),
  (9,  'demo_admin',     DATE_SUB(@now, INTERVAL 14 DAY), 'success', 'BorrowRecord', '创建借阅记录 张伟→算法导论'),
  (10, 'demo_admin',     DATE_SUB(@now, INTERVAL 8 DAY),  'info',    'BorrowRecord', '关闭借阅记录 张伟→算法导论'),
  (11, 'demo_librarian', DATE_SUB(@now, INTERVAL 3 DAY),  'success', 'BorrowRecord', '创建借阅记录 王小明→平凡的世界'),
  (12, 'demo_admin',     DATE_SUB(@now, INTERVAL 2 DAY),  'warning', 'Book',         '更新图书《C程序设计》信息'),
  (13, 'demo_admin',     DATE_SUB(@now, INTERVAL 1 DAY),  'success', 'Member',       '新增会员 周杰'),
  (14, 'demo_librarian', DATE_SUB(@now, INTERVAL 1 DAY),  'danger',  'Book',         '删除重复图书记录'),
  (15, 'demo_admin',     @now,                            'success', 'BorrowRecord', '创建借阅记录 赵丽华→时间简史');

-- ============================================================
-- 10. 评论 (comment_comment)
-- ============================================================
INSERT INTO `comment_comment` (`id`,`book_id`,`user_id`,`body`,`created_at`) VALUES
  (1,  4,  3, '三体太震撼了！第一部看得停不下来，尤其是古筝行动那段描写。', DATE_SUB(@now, INTERVAL 28 DAY)),
  (2,  4,  1, '硬科幻的巅峰之作，黑暗森林法则的设定非常精妙。', DATE_SUB(@now, INTERVAL 25 DAY)),
  (3,  1,  3, '鲁迅的文字历久弥新，《狂人日记》读了好几遍还是很有冲击力。', DATE_SUB(@now, INTERVAL 22 DAY)),
  (4,  2,  2, '红楼梦不愧是四大名著之首，每次重读都有新的感悟。', DATE_SUB(@now, INTERVAL 20 DAY)),
  (5,  3,  3, '《活着》让人泪目，余华用最朴素的语言写出了最深沉的悲剧。', DATE_SUB(@now, INTERVAL 18 DAY)),
  (6,  6,  1, '算法导论虽然厚，但是讲解非常系统，适合作为参考书反复查阅。', DATE_SUB(@now, INTERVAL 15 DAY)),
  (7,  10, 3, '霍金把复杂的物理概念讲得通俗易懂，太厉害了。', DATE_SUB(@now, INTERVAL 12 DAY)),
  (8,  13, 2, '平凡的世界很感人，孙少平的奋斗精神特别激励人。', DATE_SUB(@now, INTERVAL 10 DAY)),
  (9,  9,  1, '曼昆的经济学原理确实很适合入门，例子都很贴近生活。', DATE_SUB(@now, INTERVAL 7 DAY)),
  (10, 5,  2, 'C语言入门首选这本，虽然有些例子略旧，但基础讲得很扎实。', DATE_SUB(@now, INTERVAL 5 DAY)),
  (11, 15, 3, '吴军老师把数学和工程结合得很好，读完对搜索引擎有了更深理解。', DATE_SUB(@now, INTERVAL 3 DAY)),
  (12, 8,  1, '冯友兰的哲学简史是了解中国哲学的最佳入口，简明扼要。', DATE_SUB(@now, INTERVAL 2 DAY)),
  (13, 7,  2, '史记的文笔真的绝了，两千多年前的文字依然生动有力。', DATE_SUB(@now, INTERVAL 1 DAY)),
  (14, 4,  2, '补充一下，三体第二部《黑暗森林》是三部曲里最精彩的！', @now),
  (15, 11, 3, '艺术的故事配图很精美，读起来像在逛博物馆。', @now);
