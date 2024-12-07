/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `administration_route` (
  `administartion_route_id` int unsigned NOT NULL AUTO_INCREMENT,
  `bla_number` int unsigned NOT NULL,
  `product_number` int unsigned NOT NULL,
  `route_of_administration` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`administartion_route_id`),
  KEY `fk__administartion_route__product__idx` (`bla_number`,`product_number`),
  CONSTRAINT `fk__administartion_route__product` FOREIGN KEY (`bla_number`, `product_number`) REFERENCES `product` (`bla_number`, `product_number`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2183 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `basic_profile_view` AS SELECT 
 1 AS `proper_name`,
 1 AS `proprietary_name`,
 1 AS `novel`,
 1 AS `applicant`,
 1 AS `orphan`*/;
SET character_set_client = @saved_cs_client;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `drug` (
  `bla_number` int unsigned NOT NULL AUTO_INCREMENT,
  `proper_name` varchar(256) NOT NULL,
  `applicant` varchar(256) NOT NULL,
  `approval_date` date NOT NULL,
  `date_of_first_licensure` date DEFAULT NULL,
  `ref_product_proper_name` varchar(256) DEFAULT NULL,
  `ref_product_proprietary_name` varchar(256) DEFAULT NULL,
  `orphan_exclusivity_exp_date` date DEFAULT NULL,
  PRIMARY KEY (`bla_number`)
) ENGINE=InnoDB AUTO_INCREMENT=761426 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `product` (
  `bla_number` int unsigned NOT NULL,
  `product_number` int unsigned NOT NULL,
  `proprietary_name` varchar(256) DEFAULT NULL,
  `dosage_form` varchar(64) DEFAULT NULL,
  `strength` varchar(256) DEFAULT NULL,
  `product_presentation` varchar(64) DEFAULT NULL,
  `bla_type` varchar(64) NOT NULL,
  `marketing_status` varchar(16) NOT NULL,
  PRIMARY KEY (`bla_number`,`product_number`),
  CONSTRAINT `fk__product__drug__bla_number` FOREIGN KEY (`bla_number`) REFERENCES `drug` (`bla_number`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `rxnconso` (
  `RXAUI` int unsigned NOT NULL AUTO_INCREMENT,
  `RXCUI` int unsigned NOT NULL,
  `SAUI` int unsigned NOT NULL,
  `SCUI` int unsigned NOT NULL,
  `SAB` enum('RXNORM','MTHSPL') NOT NULL,
  `TTY` enum('BN','IN','SU','SY','PIN','TMSY','PT','DF','SCDF','MIN','SBDF','SCD','DP','PSN','SBD','MTH_RXN_DP','SCDC','SBDC','GPCK','BPCK','DFG','SCDG','SBDG','SCDFP','SBDFP','SCDGP') NOT NULL,
  `CODE` varchar(15) NOT NULL,
  `STR` varchar(3000) NOT NULL,
  PRIMARY KEY (`RXAUI`)
) ENGINE=InnoDB AUTO_INCREMENT=12930598 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `rxnrel` (
  `RUI` int unsigned NOT NULL AUTO_INCREMENT,
  `REL` enum('RO','RB','RN') NOT NULL,
  `SAB` enum('RXNORM','MTHSPL') NOT NULL,
  `STYPE` enum('AUI','CUI') NOT NULL,
  PRIMARY KEY (`RUI`)
) ENGINE=InnoDB AUTO_INCREMENT=164208255 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `rxnrel_atom` (
  `RUI` int unsigned NOT NULL,
  `RXAUI1` int unsigned NOT NULL,
  `RXAUI2` int unsigned NOT NULL,
  PRIMARY KEY (`RUI`),
  KEY `fk__rxnrel_atom__rxnconso__RXAUI1` (`RXAUI1`),
  KEY `fk__rxnrel_atom__rxnconso__RXAUI2` (`RXAUI2`),
  CONSTRAINT `fk__rxnrel_atom__rxnconso__RXAUI1` FOREIGN KEY (`RXAUI1`) REFERENCES `rxnconso` (`RXAUI`) ON DELETE CASCADE,
  CONSTRAINT `fk__rxnrel_atom__rxnconso__RXAUI2` FOREIGN KEY (`RXAUI2`) REFERENCES `rxnconso` (`RXAUI`) ON DELETE CASCADE,
  CONSTRAINT `fk__rxnrel_atom__rxnrel__RUI` FOREIGN KEY (`RUI`) REFERENCES `rxnrel` (`RUI`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `rxnrel_atom_spl` (
  `RUI` int unsigned NOT NULL,
  `RELA` enum('has_active_ingredient','has_active_moiety','has_inactive_ingredient','inactive_ingredient_of','active_ingredient_of','active_moiety_of') DEFAULT NULL,
  PRIMARY KEY (`RUI`),
  CONSTRAINT `fk__rxnrel_atom_spl__rxnrel__RUI` FOREIGN KEY (`RUI`) REFERENCES `rxnrel` (`RUI`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `rxnrel_atom_syn` (
  `RXAUI1` int unsigned NOT NULL,
  `RXAUI2` int unsigned NOT NULL,
  PRIMARY KEY (`RXAUI1`,`RXAUI2`),
  KEY `fk__rxnrel_atom_syn__rxnconso__RXAUI2` (`RXAUI2`),
  CONSTRAINT `fk__rxnrel_atom_syn__rxnconso__RXAUI1` FOREIGN KEY (`RXAUI1`) REFERENCES `rxnconso` (`RXAUI`) ON DELETE CASCADE,
  CONSTRAINT `fk__rxnrel_atom_syn__rxnconso__RXAUI2` FOREIGN KEY (`RXAUI2`) REFERENCES `rxnconso` (`RXAUI`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `rxnrel_concept` (
  `RUI` int unsigned NOT NULL,
  `RXCUI1` int unsigned NOT NULL,
  `RXCUI2` int unsigned NOT NULL,
  `RELA` enum('has_active_ingredient','has_active_moiety','has_inactive_ingredient','inactive_ingredient_of','active_ingredient_of','active_moiety_of','has_tradename','has_ingredient','tradename_of','form_of','has_part','has_precise_ingredient','has_form','has_boss','precise_ingredient_of','has_dose_form','inverse_isa','ingredient_of','dose_form_of','isa','part_of','has_ingredients','constitutes','contains','ingredients_of','consists_of','quantified_form_of','contained_in','reformulation_of','has_quantified_form','has_doseformgroup','doseformgroup_of','reformulated_to','boss_of') NOT NULL,
  PRIMARY KEY (`RUI`),
  CONSTRAINT `fk__rxnrel_concept__rxnrel__RUI` FOREIGN KEY (`RUI`) REFERENCES `rxnrel` (`RUI`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `rxnsat` (
  `RXAUI` int unsigned NOT NULL,
  `ATN` enum('RXN_BN_CARDINALITY','SPL_SET_ID','RXN_ACTIVATED','RXN_OBSOLETED','ORIG_CODE','ORIG_SOURCE','NDC','RXN_AI','RXN_AM','RXN_AVAILABLE_STRENGTH','RXN_BOSS_FROM','RXN_HUMAN_DRUG','RXTERM_FORM','DM_SPL_ID','LABELER','LABEL_TYPE','MARKETING_CATEGORY','MARKETING_EFFECTIVE_TIME_LOW','MARKETING_STATUS','OTC_MONOGRAPH_DRUG','MARKETING_EFFECTIVE_TIME_HIGH','OTC_MONOGRAPH_NOT_FINAL','COLOR','COLORTEXT','RXN_VET_DRUG','ANDA','IMPRINT_CODE','SCORE','SHAPE','SIZE','SHAPETEXT','NDA','NDA_AUTHORIZED_GENERIC','OTC_MONOGRAPH_FINAL','RXN_QUANTITY','DCSA','AMBIGUITY_FLAG','BLA','ANADA','NHRIC','CONDITIONAL_NADA','NADA','RXN_QUALITATIVE_DISTINCTION','EXEMPT_DEVICE','RXN_BOSS_STRENGTH_DENOM_UNIT','RXN_BOSS_STRENGTH_DENOM_VALUE','RXN_BOSS_STRENGTH_NUM_UNIT','RXN_BOSS_STRENGTH_NUM_VALUE','RXN_STRENGTH','RXN_IN_EXPRESSED_FLAG','PREMARKET_NOTIFICATION','PREMARKET_APPLICATION') NOT NULL,
  `ATV` varchar(500) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NOT NULL,
  `RXCUI` int unsigned NOT NULL,
  `CODE` varchar(15) NOT NULL,
  `SAB` enum('RXNORM','MTHSPL') NOT NULL,
  PRIMARY KEY (`RXAUI`,`ATN`,`ATV`),
  CONSTRAINT `fk__rxnsat__rxnconso__RXAUI` FOREIGN KEY (`RXAUI`) REFERENCES `rxnconso` (`RXAUI`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!50001 DROP VIEW IF EXISTS `basic_profile_view`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`admin`@`%` SQL SECURITY DEFINER */
/*!50001 VIEW `basic_profile_view` AS select distinct `d`.`proper_name` AS `proper_name`,`p`.`proprietary_name` AS `proprietary_name`,(case when (`p`.`bla_type` = '351(a)') then 'yes' else 'no' end) AS `novel`,`d`.`applicant` AS `applicant`,(case when (`d`.`orphan_exclusivity_exp_date` is not null) then 'yes' else 'no' end) AS `orphan` from (`drug` `d` join `product` `p` on((`d`.`bla_number` = `p`.`bla_number`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;