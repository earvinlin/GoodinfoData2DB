CREATE TABLE
  `stocks_per_and_pbr` (
    `stock_no` varchar(20) NOT NULL COMMENT '�Ѳ��N��',
    `year` varchar(10) NOT NULL COMMENT '�~��',
    `share_capital` decimal(8, 2) DEFAULT NULL COMMENT '�ѥ�(��)',
    `fin_report_score` decimal(8, 2) DEFAULT NULL COMMENT '�]������',
    `ann_high_price` decimal(8, 2) DEFAULT NULL COMMENT '�~�תѻ�-�̰�',
    `ann_low_price` decimal(8, 2) DEFAULT NULL COMMENT '�~�תѻ�-�̧C',
    `ann_end_price` decimal(8, 2) DEFAULT NULL COMMENT '�~�תѻ�-���L',
    `ann_avg_price` decimal(8, 2) DEFAULT NULL COMMENT '�~�תѻ�-����',
    `ann_price_raf` decimal(8, 2) DEFAULT NULL COMMENT '�~�תѻ�-���^',
    `ann_price_raf_pct` decimal(8, 2) DEFAULT NULL COMMENT '�~�תѻ�-���^(%)',
    `pes_statistics_eps` decimal(8, 2) DEFAULT NULL COMMENT '���q��(PER)�έp-EPS',
    `pes_statistics_high` decimal(8, 2) DEFAULT NULL COMMENT '���q��(PER)�έp-�̰�',
    `pes_statistics_low` decimal(8, 2) DEFAULT NULL COMMENT '���q��(PER)�έp-�̧C',
    `pes_statistics_avg` decimal(8, 2) DEFAULT NULL COMMENT '���q��(PER)�έp-����',
    `pbr_statistics_eps` decimal(8, 2) DEFAULT NULL COMMENT '���b��(PBR)�έp-EPS',
    `pbr_statistics_high` decimal(8, 2) DEFAULT NULL COMMENT '���b��(PBR)�έp-�̰�',
    `pbr_statistics_low` decimal(8, 2) DEFAULT NULL COMMENT '���b��(PBR)�έp-�̧C',
    `pbr_statistics_avg` decimal(8, 2) DEFAULT NULL COMMENT '���b��(PBR)�έp-����',
    PRIMARY KEY (`stock_no`, `year`)
  ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb3 COLLATE = utf8mb3_bin