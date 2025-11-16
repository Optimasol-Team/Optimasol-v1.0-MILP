CREATE DATABASE  IF NOT EXISTS `bdd_v3` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `bdd_v3`;
-- MySQL dump 10.13  Distrib 8.0.43, for Win64 (x86_64)
--
-- Host: localhost    Database: bdd_v3
-- ------------------------------------------------------
-- Server version	8.0.43

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `chauffe_eaux`
--

DROP TABLE IF EXISTS `chauffe_eaux`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `chauffe_eaux` (
  `chauffe_eau_id` int NOT NULL AUTO_INCREMENT,
  `client_id` int DEFAULT NULL,
  `capacite_litres` int DEFAULT NULL,
  `puissance_kw` decimal(5,2) DEFAULT NULL,
  PRIMARY KEY (`chauffe_eau_id`),
  KEY `client_id` (`client_id`),
  CONSTRAINT `chauffe_eaux_ibfk_1` FOREIGN KEY (`client_id`) REFERENCES `clients` (`client_id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `chauffe_eaux`
--


--
-- Table structure for table `clients`
--

DROP TABLE IF EXISTS `clients`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `clients` (
  `client_id` int NOT NULL AUTO_INCREMENT,
  `nom` varchar(100) DEFAULT NULL,
  `email` varchar(150) DEFAULT NULL,
  `latitude` decimal(10,8) DEFAULT NULL,
  `longitude` decimal(11,8) DEFAULT NULL,
  `tilt` decimal(8,2) DEFAULT NULL,
  `azimuth` decimal(8,2) DEFAULT NULL,
  `router_id` varchar(50) DEFAULT NULL,
    `pwd` varchar(50) DEFAULT NULL, 
  PRIMARY KEY (`client_id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `clients`
--


-- Table structure for table `configuration_prediction`
--

DROP TABLE IF EXISTS `configuration_prediction`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `configuration_prediction` (
  `config_id` int NOT NULL AUTO_INCREMENT,
  `chauffe_eau_id` int DEFAULT NULL,
  `step_min` int DEFAULT NULL,
  `horizon_prediction_heures` int DEFAULT NULL,
  `seuil_alerte_basse` decimal(5,2) DEFAULT NULL,
  `seuil_alerte_haute` decimal(5,2) DEFAULT NULL,
  `processor` enum('custom','default') DEFAULT 'default',
  `surface_m2` decimal(8,2) DEFAULT NULL,
  `panel_efficiency` decimal(4,3) DEFAULT NULL,
  `system_efficiency` decimal(4,3) DEFAULT NULL,
  PRIMARY KEY (`config_id`),
  KEY `chauffe_eau_id` (`chauffe_eau_id`),
  CONSTRAINT `configuration_prediction_ibfk_1` FOREIGN KEY (`chauffe_eau_id`) REFERENCES `chauffe_eaux` (`chauffe_eau_id`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `configuration_prediction`
--


--
-- Table structure for table `decision`
--

DROP TABLE IF EXISTS `decision`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `decision` (
  `id_decision` int NOT NULL AUTO_INCREMENT,
  `chauffe_eau_id` int DEFAULT NULL,
  `statut` text,
  `heure_decision` datetime DEFAULT NULL,
  `timestamp_creation` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_decision`),
  KEY `chauffe_eau_id` (`chauffe_eau_id`),
  CONSTRAINT `decision_ibfk_1` FOREIGN KEY (`chauffe_eau_id`) REFERENCES `chauffe_eaux` (`chauffe_eau_id`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `decision`
--

--
-- Table structure for table `decisions_temperature`
--

DROP TABLE IF EXISTS `decisions_temperature`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `decisions_temperature` (
  `prevision_id` int NOT NULL AUTO_INCREMENT,
  `chauffe_eau_id` int DEFAULT NULL,
  `temperature_predite` decimal(5,2) DEFAULT NULL,
  `heure_prevision` datetime DEFAULT NULL,
  `confidence` decimal(4,3) DEFAULT NULL,
  `timestamp_creation` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `modele_utilise` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`prevision_id`),
  KEY `chauffe_eau_id` (`chauffe_eau_id`),
  CONSTRAINT `decisions_temperature_ibfk_1` FOREIGN KEY (`chauffe_eau_id`) REFERENCES `chauffe_eaux` (`chauffe_eau_id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `decisions_temperature`
--

--
-- Table structure for table `donnees_meteo`
--

DROP TABLE IF EXISTS `donnees_meteo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `donnees_meteo` (
  `meteo_id` int NOT NULL AUTO_INCREMENT,
  `client_id` int DEFAULT NULL,
  `temperature_ext` decimal(5,2) DEFAULT NULL,
  `humidity` decimal(5,2) DEFAULT NULL,
  `wind_speed` decimal(5,2) DEFAULT NULL,
  `precipitation` decimal(5,2) DEFAULT NULL,
  `cloud_cover` int DEFAULT NULL,
  `weather_code` varchar(50) DEFAULT NULL,
  `heure_debut` datetime DEFAULT NULL,
  `heure_fin` datetime DEFAULT NULL,
  `source_meteo` varchar(50) DEFAULT NULL,
  `timestamp_acquisition` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `irradiance` int DEFAULT NULL,
  PRIMARY KEY (`meteo_id`),
  KEY `client_id` (`client_id`),
  CONSTRAINT `donnees_meteo_ibfk_1` FOREIGN KEY (`client_id`) REFERENCES `clients` (`client_id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `donnees_meteo`
--


-- Table structure for table `previsions_production`
--

DROP TABLE IF EXISTS `previsions_production`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `previsions_production` (
  `prevision_id` int NOT NULL AUTO_INCREMENT,
  `client_id` int DEFAULT NULL,
  `puissance_prevue_kw` decimal(8,2) DEFAULT NULL,
  `heure_prevision` datetime DEFAULT NULL,
  `timestamp_creation` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`prevision_id`),
  KEY `client_id` (`client_id`),
  CONSTRAINT `previsions_production_ibfk_1` FOREIGN KEY (`client_id`) REFERENCES `clients` (`client_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3820 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `previsions_production`
--

-- Table structure for table `production_reelle`
--

DROP TABLE IF EXISTS `production_reelle`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `production_reelle` (
  `production_id` int NOT NULL AUTO_INCREMENT,
  `client_id` int DEFAULT NULL,
  `puissance_produite_kw` decimal(8,2) DEFAULT NULL,
  `heure_production` datetime DEFAULT NULL,
  `timestamp_mesure` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`production_id`),
  KEY `client_id` (`client_id`),
  CONSTRAINT `production_reelle_ibfk_1` FOREIGN KEY (`client_id`) REFERENCES `clients` (`client_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `production_reelle`
--


--
-- Table structure for table `system_configuration`
--

DROP TABLE IF EXISTS `system_configuration`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `system_configuration` (
  `config_id` int NOT NULL AUTO_INCREMENT,
  `client_id` int DEFAULT NULL,
  `water_consumption` JSON DEFAULT NULL,
  `cold_water_temperature` decimal(4,1) DEFAULT NULL,
  `minimum_comfort_temperature_enabled` BOOLEAN DEFAULT FALSE,
  `minimum_comfort_temperature` decimal(4,1) DEFAULT NULL,
  `contract_type` enum('base','heures_creuses','tempo') DEFAULT NULL,
  `base_tariff` decimal(6,4) DEFAULT NULL,
  `hp_tariff` decimal(6,4) DEFAULT NULL,
  `hc_tariff` decimal(6,4) DEFAULT NULL,
  `comfort_schedule` json DEFAULT NULL,
  `hot_water_draws` json DEFAULT NULL,
  `off_peak_hours` json DEFAULT NULL,
  `sell_tariffs` json DEFAULT NULL,
  PRIMARY KEY (`config_id`),
  KEY `client_id` (`client_id`),
  CONSTRAINT `system_configuration_ibfk_1` FOREIGN KEY (`client_id`) REFERENCES `clients` (`client_id`)
) ENGINE=InnoDB AUTO_INCREMENT=33 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `system_configuration`
--


--
-- Table structure for table `temperatures_reelles`
--

DROP TABLE IF EXISTS `temperatures_reelles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `temperatures_reelles` (
  `mesure_id` int NOT NULL AUTO_INCREMENT,
  `chauffe_eau_id` int DEFAULT NULL,
  `temperature` decimal(5,2) DEFAULT NULL,
  `timestamp_mesure` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`mesure_id`),
  KEY `chauffe_eau_id` (`chauffe_eau_id`),
  CONSTRAINT `temperatures_reelles_ibfk_1` FOREIGN KEY (`chauffe_eau_id`) REFERENCES `chauffe_eaux` (`chauffe_eau_id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `temperatures_reelles`
--


