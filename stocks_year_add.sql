CREATE TABLE
`stocks_year_add` (
`stock_no` varchar(20) NOT NULL COMMENT '股票代號',
`year` varchar(10) NOT NULL COMMENT '年度',
`op_income_amt` decimal(8, 2) DEFAULT NULL COMMENT '營業收入_金額(億)', 
`op_income_iod` decimal(8, 2) DEFAULT NULL COMMENT '營業收入_增減(億)', 
`op_income_iod_pct` decimal(8, 2) DEFAULT NULL COMMENT '營業收入_增減(%)', 
`op_gp_amt` decimal(8, 2) DEFAULT NULL COMMENT '營業毛利_金額(億)', 
`op_gp_iod` decimal(8, 2) DEFAULT NULL COMMENT '營業毛利_增減(億)', 
`op_gp_iod_pct` decimal(8, 2) DEFAULT NULL COMMENT '營業毛利_增減(%)', 
`gp_margin_pct` decimal(8, 2) DEFAULT NULL COMMENT '毛利率_毛利(%)', 
`gp_margin_iod` decimal(8, 2) DEFAULT NULL COMMENT '毛利率_增減數', 
`op_profit_amt` decimal(8, 2) DEFAULT NULL COMMENT '營業利益_金額(億)', 
`op_profit_iod` decimal(8, 2) DEFAULT NULL COMMENT '營業利益_增減(億)', 
`op_profit_iod_pct` decimal(8, 2) DEFAULT NULL COMMENT '營業利益_增減(%)', 
`profit_margin_pct` decimal(8, 2) DEFAULT NULL COMMENT '營益率_營益(%)', 
`profit_margin_iod` decimal(8, 2) DEFAULT NULL COMMENT '營益率_增減數', 	
`net_profit_at_amt` decimal(8, 2) DEFAULT NULL COMMENT '稅後淨利_金額(億)', 	
`net_profit_at_iod` decimal(8, 2) DEFAULT NULL COMMENT '稅後淨利_增減(億)', 	
`net_profit_at_iod_pct` decimal(8, 2) DEFAULT NULL COMMENT '稅後淨利_增減(%)', 
`net_profit_pct` decimal(8, 2) DEFAULT NULL COMMENT '稅後淨利率_淨利(%)', 
`net_profit_pct_iod` decimal(8, 2) DEFAULT NULL COMMENT '稅後淨利率_增減數', 	
`eps` decimal(8, 2) DEFAULT NULL COMMENT '每股盈餘_PES(元)', 	
`eps_iod` decimal(8, 2) DEFAULT NULL COMMENT '每股盈餘_增減(元)', 
`roe` decimal(8, 2) DEFAULT NULL COMMENT 'ROE_ROE(%)', 
`roe_iod` decimal(8, 2) DEFAULT NULL COMMENT 'ROE_增減數', 
`roa` decimal(8, 2) DEFAULT NULL COMMENT 'ROA_ROA(%)', 
`roa_iod` decimal(8, 2) DEFAULT NULL COMMENT 'ROA_增減數', 
    PRIMARY KEY (`stock_no`, `year`)
  ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb3 COLLATE = utf8mb3_bin
