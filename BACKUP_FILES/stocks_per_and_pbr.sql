CREATE TABLE
  `stocks_per_and_pbr` (
    `stock_no` varchar(20) NOT NULL COMMENT '布腹',
    `year` varchar(10) NOT NULL COMMENT '',
    `share_capital` decimal(8, 2) DEFAULT NULL COMMENT 'セ(货)',
    `fin_report_score` decimal(8, 2) DEFAULT NULL COMMENT '癩厨だ计',
    `ann_high_price` decimal(8, 2) DEFAULT NULL COMMENT '基-程蔼',
    `ann_low_price` decimal(8, 2) DEFAULT NULL COMMENT '基-程',
    `ann_end_price` decimal(8, 2) DEFAULT NULL COMMENT '基-Μ絃',
    `ann_avg_price` decimal(8, 2) DEFAULT NULL COMMENT '基-キА',
    `ann_price_raf` decimal(8, 2) DEFAULT NULL COMMENT '基-害禴',
    `ann_price_raf_pct` decimal(8, 2) DEFAULT NULL COMMENT '基-害禴(%)',
    `pes_statistics_eps` decimal(8, 2) DEFAULT NULL COMMENT 'セ痲ゑ(PER)参璸-EPS',
    `pes_statistics_high` decimal(8, 2) DEFAULT NULL COMMENT 'セ痲ゑ(PER)参璸-程蔼',
    `pes_statistics_low` decimal(8, 2) DEFAULT NULL COMMENT 'セ痲ゑ(PER)参璸-程',
    `pes_statistics_avg` decimal(8, 2) DEFAULT NULL COMMENT 'セ痲ゑ(PER)参璸-キА',
    `pbr_statistics_eps` decimal(8, 2) DEFAULT NULL COMMENT 'セ瞓ゑ(PBR)参璸-EPS',
    `pbr_statistics_high` decimal(8, 2) DEFAULT NULL COMMENT 'セ瞓ゑ(PBR)参璸-程蔼',
    `pbr_statistics_low` decimal(8, 2) DEFAULT NULL COMMENT 'セ瞓ゑ(PBR)参璸-程',
    `pbr_statistics_avg` decimal(8, 2) DEFAULT NULL COMMENT 'セ瞓ゑ(PBR)参璸-キА',
    PRIMARY KEY (`stock_no`, `year`)
  ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb3 COLLATE = utf8mb3_bin