-- MySQL dump 10.13  Distrib 5.7.19, for Linux (x86_64)
--
-- Host: 127.0.0.1    Database: bk_fta_solutions
-- ------------------------------------------------------
-- Server version	5.7.18

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

CREATE DATABASE IF NOT EXISTS `bk_fta_solutions` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;

USE `bk_fta_solutions`;

--
-- Table structure for table `account_bkuser`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `account_bkuser` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(128) NOT NULL,
  `chname` varchar(254) NOT NULL,
  `company` varchar(128) NOT NULL,
  `qq` varchar(32) NOT NULL,
  `phone` varchar(64) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `date_joined` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `account_bkuser`
--

LOCK TABLES `account_bkuser` WRITE;
/*!40000 ALTER TABLE `account_bkuser` DISABLE KEYS */;
INSERT INTO `account_bkuser` VALUES (1,'','2017-09-05 19:14:25',1,'admin','','','','','',1,'2017-09-05 19:14:25'),(2,'!XglmoURBjRa8vVb7r62TzYFFKDd7pFy4lhNAckKq',NULL,0,'AnonymousUser','','','','','',0,'2017-09-05 19:14:41');
/*!40000 ALTER TABLE `account_bkuser` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `account_bkuser_groups`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `account_bkuser_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `bkuser_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `bkuser_id` (`bkuser_id`,`group_id`),
  KEY `account_bkuser_groups_group_id_62e6d4600781d550_fk_auth_group_id` (`group_id`),
  CONSTRAINT `account_bkuser_g_bkuser_id_2afe1b401266c2ba_fk_account_bkuser_id` FOREIGN KEY (`bkuser_id`) REFERENCES `account_bkuser` (`id`),
  CONSTRAINT `account_bkuser_groups_group_id_62e6d4600781d550_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `account_bkuser_groups`
--

LOCK TABLES `account_bkuser_groups` WRITE;
/*!40000 ALTER TABLE `account_bkuser_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `account_bkuser_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `account_bkuser_user_permissions`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `account_bkuser_user_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `bkuser_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `bkuser_id` (`bkuser_id`,`permission_id`),
  KEY `account_bkus_permission_id_d5bec30ce864e6d_fk_auth_permission_id` (`permission_id`),
  CONSTRAINT `account_bkus_permission_id_d5bec30ce864e6d_fk_auth_permission_id` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `account_bkuser_u_bkuser_id_726503c76778809c_fk_account_bkuser_id` FOREIGN KEY (`bkuser_id`) REFERENCES `account_bkuser` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `account_bkuser_user_permissions`
--

LOCK TABLES `account_bkuser_user_permissions` WRITE;
/*!40000 ALTER TABLE `account_bkuser_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `account_bkuser_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(80) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `group_id` (`group_id`,`permission_id`),
  KEY `auth_group__permission_id_1f49ccbbdc69d2fc_fk_auth_permission_id` (`permission_id`),
  CONSTRAINT `auth_group__permission_id_1f49ccbbdc69d2fc_fk_auth_permission_id` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permission_group_id_689710a9a73b7457_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `content_type_id` (`content_type_id`,`codename`),
  CONSTRAINT `auth__content_type_id_508cf46651277a81_fk_django_content_type_id` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=141 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add permission',1,'add_permission'),(2,'Can change permission',1,'change_permission'),(3,'Can delete permission',1,'delete_permission'),(4,'Can add group',2,'add_group'),(5,'Can change group',2,'change_group'),(6,'Can delete group',2,'delete_group'),(7,'Can add content type',3,'add_contenttype'),(8,'Can change content type',3,'change_contenttype'),(9,'Can delete content type',3,'delete_contenttype'),(10,'Can add session',4,'add_session'),(11,'Can change session',4,'change_session'),(12,'Can delete session',4,'delete_session'),(13,'Can add site',5,'add_site'),(14,'Can change site',5,'change_site'),(15,'Can delete site',5,'delete_site'),(16,'Can add log entry',6,'add_logentry'),(17,'Can change log entry',6,'change_logentry'),(18,'Can delete log entry',6,'delete_logentry'),(19,'Can add user object permission',7,'add_userobjectpermission'),(20,'Can change user object permission',7,'change_userobjectpermission'),(21,'Can delete user object permission',7,'delete_userobjectpermission'),(22,'Can add group object permission',8,'add_groupobjectpermission'),(23,'Can change group object permission',8,'change_groupobjectpermission'),(24,'Can delete group object permission',8,'delete_groupobjectpermission'),(25,'Can add user',9,'add_bkuser'),(26,'Can change user',9,'change_bkuser'),(27,'Can delete user',9,'delete_bkuser'),(28,'Can add 流程审批',10,'add_approve'),(29,'Can change 流程审批',10,'change_approve'),(30,'Can delete 流程审批',10,'delete_approve'),(31,'Can add api access',11,'add_apiaccess'),(32,'Can change api access',11,'change_apiaccess'),(33,'Can delete api access',11,'delete_apiaccess'),(34,'Can add api key',12,'add_apikey'),(35,'Can change api key',12,'change_apikey'),(36,'Can delete api key',12,'delete_apikey'),(37,'Can add solution',13,'add_solution'),(38,'Can change solution',13,'change_solution'),(39,'Can delete solution',13,'delete_solution'),(40,'Can add alarm def',14,'add_alarmdef'),(41,'Can change alarm def',14,'change_alarmdef'),(42,'Can delete alarm def',14,'delete_alarmdef'),(43,'Can add alarm type',15,'add_alarmtype'),(44,'Can change alarm type',15,'change_alarmtype'),(45,'Can delete alarm type',15,'delete_alarmtype'),(46,'Can add world',16,'add_world'),(47,'Can change world',16,'change_world'),(48,'Can delete world',16,'delete_world'),(49,'Can add alarm instance',17,'add_alarminstance'),(50,'Can change alarm instance',17,'change_alarminstance'),(51,'Can delete alarm instance',17,'delete_alarminstance'),(52,'Can add alarm instance backup',18,'add_alarminstancebackup'),(53,'Can change alarm instance backup',18,'change_alarminstancebackup'),(54,'Can delete alarm instance backup',18,'delete_alarminstancebackup'),(55,'Can add incident def',19,'add_incidentdef'),(56,'Can change incident def',19,'change_incidentdef'),(57,'Can delete incident def',19,'delete_incidentdef'),(58,'Can add advice def',20,'add_advicedef'),(59,'Can change advice def',20,'change_advicedef'),(60,'Can delete advice def',20,'delete_advicedef'),(61,'Can add advice',21,'add_advice'),(62,'Can change advice',21,'change_advice'),(63,'Can delete advice',21,'delete_advice'),(64,'Can add advice fta def',22,'add_adviceftadef'),(65,'Can change advice fta def',22,'change_adviceftadef'),(66,'Can delete advice fta def',22,'delete_adviceftadef'),(67,'Can add incident',23,'add_incident'),(68,'Can change incident',23,'change_incident'),(69,'Can delete incident',23,'delete_incident'),(70,'Can add incident alarm',24,'add_incidentalarm'),(71,'Can change incident alarm',24,'change_incidentalarm'),(72,'Can delete incident alarm',24,'delete_incidentalarm'),(73,'Can add context',25,'add_context'),(74,'Can change context',25,'change_context'),(75,'Can delete context',25,'delete_context'),(76,'Can add user biz',26,'add_userbiz'),(77,'Can change user biz',26,'change_userbiz'),(78,'Can delete user biz',26,'delete_userbiz'),(79,'Can add biz conf',27,'add_bizconf'),(80,'Can change biz conf',27,'change_bizconf'),(81,'Can delete biz conf',27,'delete_bizconf'),(82,'Can add 配置项',28,'add_conf'),(83,'Can change 配置项',28,'change_conf'),(84,'Can delete 配置项',28,'delete_conf'),(85,'Can add 数据修改日志',29,'add_datachanglog'),(86,'Can change 数据修改日志',29,'change_datachanglog'),(87,'Can delete 数据修改日志',29,'delete_datachanglog'),(88,'Can add alarm instance log',30,'add_alarminstancelog'),(89,'Can change alarm instance log',30,'change_alarminstancelog'),(90,'Can delete alarm instance log',30,'delete_alarminstancelog'),(91,'Can add out of scope archive',31,'add_outofscopearchive'),(92,'Can change out of scope archive',31,'change_outofscopearchive'),(93,'Can delete out of scope archive',31,'delete_outofscopearchive'),(94,'Can add ignore alarm',32,'add_ignorealarm'),(95,'Can change ignore alarm',32,'change_ignorealarm'),(96,'Can delete ignore alarm',32,'delete_ignorealarm'),(97,'Can add kpi cache',33,'add_kpicache'),(98,'Can change kpi cache',33,'change_kpicache'),(99,'Can delete kpi cache',33,'delete_kpicache'),(100,'Can add alarm instance archive',34,'add_alarminstancearchive'),(101,'Can change alarm instance archive',34,'change_alarminstancearchive'),(102,'Can delete alarm instance archive',34,'delete_alarminstancearchive'),(103,'Can add eagle eye',35,'add_eagleeye'),(104,'Can change eagle eye',35,'change_eagleeye'),(105,'Can delete eagle eye',35,'delete_eagleeye'),(106,'Can add inc related alarm',36,'add_increlatedalarm'),(107,'Can change inc related alarm',36,'change_increlatedalarm'),(108,'Can delete inc related alarm',36,'delete_increlatedalarm'),(109,'Can add inc order',37,'add_incorder'),(110,'Can change inc order',37,'change_incorder'),(111,'Can delete inc order',37,'delete_incorder'),(112,'Can add qcloud owner info',38,'add_qcloudownerinfo'),(113,'Can change qcloud owner info',38,'change_qcloudownerinfo'),(114,'Can delete qcloud owner info',38,'delete_qcloudownerinfo'),(115,'Can add approve callback',39,'add_approvecallback'),(116,'Can change approve callback',39,'change_approvecallback'),(117,'Can delete approve callback',39,'delete_approvecallback'),(118,'Can add user action',40,'add_useraction'),(119,'Can change user action',40,'change_useraction'),(120,'Can delete user action',40,'delete_useraction'),(121,'Can add 添加告警应用',41,'add_alarmapplication'),(122,'Can change 添加告警应用',41,'change_alarmapplication'),(123,'Can delete 添加告警应用',41,'delete_alarmapplication'),(124,'Can add 业务 Business',42,'add_business'),(125,'Can change 业务 Business',42,'change_business'),(126,'Can delete 业务 Business',42,'delete_business'),(127,'Can view business',42,'view_business'),(128,'Can manage business',42,'manage_business'),(129,'Can add 用户默认业务 UserBusiness',43,'add_userbusiness'),(130,'Can change 用户默认业务 UserBusiness',43,'change_userbusiness'),(131,'Can delete 用户默认业务 UserBusiness',43,'delete_userbusiness'),(132,'Can add 业务用户组 BusinessGroupMembership',44,'add_businessgroupmembership'),(133,'Can change 业务用户组 BusinessGroupMembership',44,'change_businessgroupmembership'),(134,'Can delete 业务用户组 BusinessGroupMembership',44,'delete_businessgroupmembership'),(135,'Can add 用户登录日志',45,'add_loignlog'),(136,'Can change 用户登录日志',45,'change_loignlog'),(137,'Can delete 用户登录日志',45,'delete_loignlog'),(138,'Can add 用户活动记录',46,'add_useractivitylog'),(139,'Can change 用户活动记录',46,'change_useractivitylog'),(140,'Can delete 用户活动记录',46,'delete_useractivitylog');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `djang_content_type_id_697914295151027a_fk_django_content_type_id` (`content_type_id`),
  KEY `django_admin_log_user_id_52fdd58701c5f563_fk_account_bkuser_id` (`user_id`),
  CONSTRAINT `djang_content_type_id_697914295151027a_fk_django_content_type_id` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_52fdd58701c5f563_fk_account_bkuser_id` FOREIGN KEY (`user_id`) REFERENCES `account_bkuser` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_45f3b1d93ec8c61c_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=47 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (9,'account','bkuser'),(6,'admin','logentry'),(2,'auth','group'),(1,'auth','permission'),(3,'contenttypes','contenttype'),(21,'fta_solutions_app','advice'),(20,'fta_solutions_app','advicedef'),(22,'fta_solutions_app','adviceftadef'),(41,'fta_solutions_app','alarmapplication'),(14,'fta_solutions_app','alarmdef'),(17,'fta_solutions_app','alarminstance'),(34,'fta_solutions_app','alarminstancearchive'),(18,'fta_solutions_app','alarminstancebackup'),(30,'fta_solutions_app','alarminstancelog'),(15,'fta_solutions_app','alarmtype'),(39,'fta_solutions_app','approvecallback'),(27,'fta_solutions_app','bizconf'),(28,'fta_solutions_app','conf'),(25,'fta_solutions_app','context'),(29,'fta_solutions_app','datachanglog'),(35,'fta_solutions_app','eagleeye'),(32,'fta_solutions_app','ignorealarm'),(23,'fta_solutions_app','incident'),(24,'fta_solutions_app','incidentalarm'),(19,'fta_solutions_app','incidentdef'),(37,'fta_solutions_app','incorder'),(36,'fta_solutions_app','increlatedalarm'),(33,'fta_solutions_app','kpicache'),(31,'fta_solutions_app','outofscopearchive'),(38,'fta_solutions_app','qcloudownerinfo'),(13,'fta_solutions_app','solution'),(40,'fta_solutions_app','useraction'),(26,'fta_solutions_app','userbiz'),(16,'fta_solutions_app','world'),(8,'guardian','groupobjectpermission'),(7,'guardian','userobjectpermission'),(42,'permission','business'),(44,'permission','businessgroupmembership'),(45,'permission','loignlog'),(43,'permission','userbusiness'),(4,'sessions','session'),(5,'sites','site'),(11,'tastypie','apiaccess'),(12,'tastypie','apikey'),(46,'user_activity_log','useractivitylog'),(10,'wechat','approve');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_migrations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=61 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2017-09-05 19:14:23'),(2,'contenttypes','0002_remove_content_type_name','2017-09-05 19:14:24'),(3,'auth','0001_initial','2017-09-05 19:14:24'),(4,'auth','0002_alter_permission_name_max_length','2017-09-05 19:14:24'),(5,'auth','0003_alter_user_email_max_length','2017-09-05 19:14:24'),(6,'auth','0004_alter_user_username_opts','2017-09-05 19:14:24'),(7,'auth','0005_alter_user_last_login_null','2017-09-05 19:14:24'),(8,'auth','0006_require_contenttypes_0002','2017-09-05 19:14:24'),(9,'account','0001_initial','2017-09-05 19:14:25'),(10,'account','0002_initial_user_data','2017-09-05 19:14:25'),(11,'admin','0001_initial','2017-09-05 19:14:25'),(12,'user_activity_log','0001_initial','2017-09-05 19:14:26'),(13,'user_activity_log','0002_auto_20170414_1800','2017-09-05 19:14:26'),(14,'fta_solutions_app','0001_initial','2017-09-05 19:14:30'),(15,'fta_solutions_app','0002_auto_20170320_1959','2017-09-05 19:14:30'),(16,'fta_solutions_app','0003_auto_20170322_2211','2017-09-05 19:14:31'),(17,'fta_solutions_app','0004_auto_20170405_1154','2017-09-05 19:14:31'),(18,'fta_solutions_app','0005_auto_20170412_1556','2017-09-05 19:14:31'),(19,'fta_solutions_app','0006_auto_20170414_1928','2017-09-05 19:14:31'),(20,'fta_solutions_app','0007_auto_20170417_1151','2017-09-05 19:14:31'),(21,'fta_solutions_app','0008_auto_20170417_1450','2017-09-05 19:14:31'),(22,'fta_solutions_app','0009_auto_20170418_1141','2017-09-05 19:14:31'),(23,'fta_solutions_app','0006_auto_20170414_1627','2017-09-05 19:14:31'),(24,'fta_solutions_app','0010_merge','2017-09-05 19:14:31'),(25,'fta_solutions_app','0011_auto_20170505_1048','2017-09-05 19:14:32'),(26,'fta_solutions_app','0012_alarmtype','2017-09-05 19:14:32'),(27,'fta_solutions_app','0013_auto_20170509_1718','2017-09-05 19:14:32'),(28,'fta_solutions_app','0014_init_conf','2017-09-05 19:14:32'),(29,'fta_solutions_app','0015_auto_20170510_1721','2017-09-05 19:14:32'),(30,'fta_solutions_app','0016_init_alarm_application','2017-09-05 19:14:32'),(31,'fta_solutions_app','0017_init_fixture','2017-09-05 19:14:33'),(32,'fta_solutions_app','0018_init_wechat_conf','2017-09-05 19:14:33'),(33,'fta_solutions_app','0019_auto_20170525_1553','2017-09-05 19:14:33'),(34,'fta_solutions_app','0020_auto_20170608_1057','2017-09-05 19:14:34'),(35,'fta_solutions_app','0021_alarmapplication_activate_time','2017-09-05 19:14:34'),(36,'fta_solutions_app','0022_init_alarm_application','2017-09-05 19:14:34'),(37,'fta_solutions_app','0023_auto_20170619_1028','2017-09-05 19:14:34'),(38,'fta_solutions_app','0024_auto_20170620_1440','2017-09-05 19:14:34'),(39,'fta_solutions_app','0025_auto_20170620_1508','2017-09-05 19:14:34'),(40,'fta_solutions_app','0026_auto_20170620_1529','2017-09-05 19:14:34'),(41,'fta_solutions_app','0027_auto_20170620_2139','2017-09-05 19:14:34'),(42,'fta_solutions_app','0028_init_advice_fta_def','2017-09-05 19:14:35'),(43,'fta_solutions_app','0029_auto_20170725_1709','2017-09-05 19:14:35'),(44,'fta_solutions_app','0030_auto_20170727_1600','2017-09-05 19:14:35'),(45,'fta_solutions_app','0031_auto_20170807_1644','2017-09-05 19:14:36'),(46,'fta_solutions_app','0031_auto_20170802_1804','2017-09-05 19:14:36'),(47,'fta_solutions_app','0031_auto_20170802_init_alarmtype','2017-09-05 19:14:36'),(48,'fta_solutions_app','0032_merge','2017-09-05 19:14:36'),(49,'fta_solutions_app','0033_zabbix_icmpping_fix','2017-09-05 19:14:36'),(50,'fta_solutions_app','0034_auto_20170829_1122','2017-09-05 19:14:38'),(51,'fta_solutions_app','0035_auto_20170829_1713','2017-09-05 19:14:38'),(52,'fta_solutions_app','0036_fix_solution_codename_1708301523','2017-09-05 19:14:38'),(53,'fta_solutions_app','0037_auto_20170830_1738','2017-09-05 19:14:38'),(54,'guardian','0001_initial','2017-09-05 19:14:39'),(55,'permission','0001_initial','2017-09-05 19:14:40'),(56,'permission','0002_loignlog','2017-09-05 19:14:40'),(57,'sessions','0001_initial','2017-09-05 19:14:40'),(58,'sites','0001_initial','2017-09-05 19:14:40'),(59,'tastypie','0001_initial','2017-09-05 19:14:41'),(60,'wechat','0001_initial','2017-09-05 19:14:41');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_de54fa62` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_site`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_site` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `domain` varchar(100) NOT NULL,
  `name` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_site`
--

LOCK TABLES `django_site` WRITE;
/*!40000 ALTER TABLE `django_site` DISABLE KEYS */;
INSERT INTO `django_site` VALUES (1,'example.com','example.com');
/*!40000 ALTER TABLE `django_site` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fta_solutions_app_advice`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `fta_solutions_app_advice` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `advice_def_id` int(11) NOT NULL,
  `cc_biz_id` int(11) NOT NULL,
  `subject` varchar(128) NOT NULL,
  `alarm_num` int(11) NOT NULL,
  `alarm_start_time` date NOT NULL,
  `alarm_end_time` date NOT NULL,
  `status` varchar(32) NOT NULL,
  `comment` longtext,
  `create_time` datetime NOT NULL,
  `operator` varchar(128) DEFAULT NULL,
  `modify_time` datetime DEFAULT NULL,
  `advice_fta_def_id` int(11),
  `alarminstance_id` int(11),
  `offline_handle` varchar(32) NOT NULL,
  `offline_time` datetime NOT NULL,
  `offline_user` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fta_solutions_app_advice_bed15c1d` (`advice_def_id`),
  KEY `fta_solutions_app_advice_b16a6265` (`create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fta_solutions_app_advice`
--

LOCK TABLES `fta_solutions_app_advice` WRITE;
/*!40000 ALTER TABLE `fta_solutions_app_advice` DISABLE KEYS */;
/*!40000 ALTER TABLE `fta_solutions_app_advice` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fta_solutions_app_advicedef`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `fta_solutions_app_advicedef` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `codename` varchar(128) NOT NULL,
  `description` longtext NOT NULL,
  `is_enabled` tinyint(1) NOT NULL,
  `cc_biz_id` int(11) NOT NULL,
  `subject_type` varchar(64) NOT NULL,
  `check_type` varchar(64) NOT NULL,
  `check_sub_type` varchar(128) NOT NULL,
  `interval` int(11) NOT NULL,
  `threshold` int(11) NOT NULL,
  `advice_type` varchar(64) NOT NULL,
  `advice` longtext NOT NULL,
  `create_time` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fta_solutions_app_advicedef`
--

LOCK TABLES `fta_solutions_app_advicedef` WRITE;
/*!40000 ALTER TABLE `fta_solutions_app_advicedef` DISABLE KEYS */;
INSERT INTO `fta_solutions_app_advicedef` VALUES (1,'host-down-weekly','7天内|同一主机|产生3+条严重告警，应产生硬件待优化事件进行后续跟踪。',1,0,'host','alarm','ZABBIX-icmping*',7,3,'hardware','确认主机是否存在硬件故障，需要做下线或者替换操作','2017-09-05 19:14:33'),(2,'host-down-weekly','7天内|同一主机|产生3+条严重告警，应产生硬件待优化事件进行后续跟踪。',1,0,'host','alarm','NAGIOS-ping',7,3,'hardware','确认主机是否存在硬件故障，需要做下线或者替换操作','2017-09-05 19:14:33'),(3,'disk-readonly-weekly','7天内|同一主机|产生3+条硬盘只读告警，应产生硬件待优化事件进行人工确认。',1,0,'host','alarm','BASE_ALARM_3',7,3,'hardware','提单请现场确认主机硬件是否故障','2017-09-05 19:14:33'),(4,'disk-full-weekly','7天内|同一主机|产生3+条磁盘满告警，应产生运维待优化事件进行后续跟踪。',1,0,'host','alarm','OPEN-FALCON-open-falcon-df.*',7,3,'ops','1、请检查当前的磁盘清理策略确实是否需要调整\n2、确认该模块当前机型的硬盘空间是否合理','2017-09-05 19:14:33'),(5,'disk-full-weekly','7天内|同一主机|产生3+条磁盘满告警，应产生运维待优化事件进行后续跟踪。',1,0,'host','alarm','ZABBIX-vfs.fs.*',7,3,'ops','1、请检查当前的磁盘清理策略确实是否需要调整\n2、确认该模块当前机型的硬盘空间是否合理','2017-09-05 19:14:33'),(6,'disk-full-weekly','7天内|同一主机|产生3+条磁盘满告警，应产生运维待优化事件进行后续跟踪。',1,0,'host','alarm','BASE_ALARM_6',7,3,'ops','1、请检查当前的磁盘清理策略确实是否需要调整\n2、确认该模块当前机型的硬盘空间是否合理','2017-09-05 19:14:33'),(7,'disk-full-monthly','30天内|同一主机|产生5+条磁盘满告警，应产生运维待优化事件进行后续跟踪。',1,0,'host','alarm','OPEN-FALCON-open-falcon-df.*',30,5,'ops','1、请检查当前的磁盘清理策略确实是否需要调整\n2、确认该模块当前机型的硬盘空间是否合理','2017-09-05 19:14:33'),(8,'disk-full-monthly','30天内|同一主机|产生5+条磁盘满告警，应产生运维待优化事件进行后续跟踪。',1,0,'host','alarm','ZABBIX-vfs.fs.*',30,5,'ops','1、请检查当前的磁盘清理策略确实是否需要调整\n2、确认该模块当前机型的硬盘空间是否合理','2017-09-05 19:14:33'),(9,'disk-full-monthly','30天内|同一主机|产生5+条磁盘满告警，应产生运维待优化事件进行后续跟踪。',1,0,'host','alarm','BASE_ALARM_6',30,5,'ops','1、请检查当前的磁盘清理策略确实是否需要调整\n2、确认该模块当前机型的硬盘空间是否合理','2017-09-05 19:14:33'),(10,'disk-full-daily','1天内|同一主机|产生2+条磁盘满告警，应产生运维待优化事件进行后续跟踪。',1,0,'host','alarm','OPEN-FALCON-open-falcon-df.*',1,2,'ops','1、请检查当前的磁盘清理策略确实是否需要调整\n2、确认该模块当前机型的硬盘空间是否合理','2017-09-05 19:14:33'),(11,'disk-full-daily','1天内|同一主机|产生2+条磁盘满告警，应产生运维待优化事件进行后续跟踪。',1,0,'host','alarm','ZABBIX-vfs.fs.*',1,2,'ops','1、请检查当前的磁盘清理策略确实是否需要调整\n2、确认该模块当前机型的硬盘空间是否合理','2017-09-05 19:14:33'),(12,'disk-full-daily','1天内|同一主机|产生2+条磁盘满告警，应产生运维待优化事件进行后续跟踪。',1,0,'host','alarm','BASE_ALARM_6',1,2,'ops','1、请检查当前的磁盘清理策略确实是否需要调整\n2、确认该模块当前机型的硬盘空间是否合理','2017-09-05 19:14:33'),(13,'disk-readonly-monthly','30天内|同一主机|产生3+条硬盘只读告警，应产生硬件待优化事件进行后续跟踪。',1,0,'host','alarm','BASE_ALARM_3',30,3,'hardware','提单请现场确认主机硬件是否故障','2017-09-05 19:14:33'),(14,'disk-readonly-daily','1天内|同一主机|产生2+条硬盘只读告警，应产生硬件待优化事件进行人工确认。',1,0,'host','alarm','BASE_ALARM_3',1,2,'hardware','提单请现场确认主机硬件是否故障','2017-09-05 19:14:33'),(15,'host-down-daily','1天内|同一主机|产生2+条严重告警，应产生硬件待优化事件进行后续跟踪。',1,0,'host','alarm','ZABBIX-icmping*',1,2,'hardware','确认主机是否存在硬件故障，需要做下线或者替换操作','2017-09-05 19:14:33'),(16,'host-down-daily','1天内|同一主机|产生2+条严重告警，应产生硬件待优化事件进行后续跟踪。',1,0,'host','alarm','NAGIOS-ping',1,2,'hardware','确认主机是否存在硬件故障，需要做下线或者替换操作','2017-09-05 19:14:33'),(17,'host-down-monthly','30天内|同一主机|产生5+条严重告警，应产生硬件待优化事件进行后续跟踪。',1,0,'host','alarm','ZABBIX-icmping*',30,5,'hardware','确认主机是否存在硬件故障，需要做下线或者替换操作','2017-09-05 19:14:33'),(18,'host-down-monthly','30天内|同一主机|产生5+条严重告警，应产生硬件待优化事件进行后续跟踪。',1,0,'host','alarm','NAGIOS-ping',30,5,'hardware','确认主机是否存在硬件故障，需要做下线或者替换操作','2017-09-05 19:14:33');
/*!40000 ALTER TABLE `fta_solutions_app_advicedef` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fta_solutions_app_adviceftadef`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `fta_solutions_app_adviceftadef` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `advice_def_id` int(11) NOT NULL,
  `is_enabled` tinyint(1) NOT NULL,
  `is_deleted` tinyint(1) NOT NULL,
  `cc_biz_id` int(11) NOT NULL,
  `module` longtext NOT NULL,
  `topo_set` longtext NOT NULL,
  `set_names` longtext NOT NULL,
  `module_names` longtext NOT NULL,
  `responsible` varchar(255) DEFAULT NULL,
  `title` varchar(128) DEFAULT NULL,
  `description` longtext,
  `notify` longtext NOT NULL,
  `solution_id` int(11) DEFAULT NULL,
  `timeout` int(11) NOT NULL,
  `exclude` longtext,
  `handle_type` varchar(10) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fta_solutions_app_adviceftadef_bed15c1d` (`advice_def_id`),
  KEY `fta_solutions_app_adviceftadef_5b14b3ac` (`cc_biz_id`),
  KEY `fta_solutions_app_adviceftadef_7a8d8e6e` (`solution_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fta_solutions_app_adviceftadef`
--

LOCK TABLES `fta_solutions_app_adviceftadef` WRITE;
/*!40000 ALTER TABLE `fta_solutions_app_adviceftadef` DISABLE KEYS */;
INSERT INTO `fta_solutions_app_adviceftadef` VALUES (1,17,1,0,0,'','','','空闲机',NULL,NULL,'内置策略','{\n        \"begin_notify_wechat\":true,\n        \"begin_notify_mail\":true,\n        \"begin_notify_sms\":false,\n        \"begin_notify_im\":false,\n        \"begin_notify_phone\":false,\n        \"success_notify_wechat\":true,\n        \"success_notify_mail\":true,\n        \"success_notify_sms\":false,\n        \"success_notify_im\":false,\n        \"success_notify_phone\":false,\n        \"failure_notify_wechat\":true,\n        \"failure_notify_mail\":true,\n        \"failure_notify_sms\":false,\n        \"failure_notify_im\":false,\n        \"failure_notify_phone\":false,\n        \"to_extra\":false,\n        \"to_role\":true\n    }',36,40,'','solution');
/*!40000 ALTER TABLE `fta_solutions_app_adviceftadef` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fta_solutions_app_alarmapplication`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `fta_solutions_app_alarmapplication` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `source_type` varchar(64) NOT NULL,
  `cc_biz_id` int(11) NOT NULL,
  `app_name` varchar(255) NOT NULL,
  `app_id` varchar(255) NOT NULL,
  `app_secret` varchar(255) NOT NULL,
  `create_time` datetime NOT NULL,
  `create_user` varchar(128) NOT NULL,
  `update_time` datetime NOT NULL,
  `update_user` varchar(128) NOT NULL,
  `is_enabled` tinyint(1) NOT NULL,
  `is_deleted` tinyint(1) NOT NULL,
  `extra` longtext,
  `exclude` longtext NOT NULL,
  `app_method` varchar(10),
  `app_url` longtext,
  `activate_time` datetime DEFAULT NULL,
  `empty_begin_time` datetime,
  `empty_num` int(11),
  `exception_begin_time` datetime,
  `exception_data` longtext,
  `exception_num` int(11),
  `exception_max_num` int(11),
  PRIMARY KEY (`id`),
  UNIQUE KEY `app_id` (`app_id`),
  UNIQUE KEY `app_secret` (`app_secret`),
  KEY `fta_solutions_app_alarmapplication_5b14b3ac` (`cc_biz_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fta_solutions_app_alarmapplication`
--

LOCK TABLES `fta_solutions_app_alarmapplication` WRITE;
/*!40000 ALTER TABLE `fta_solutions_app_alarmapplication` DISABLE KEYS */;
INSERT INTO `fta_solutions_app_alarmapplication` VALUES (1,'ALERT',0,'蓝鲸监控的告警源','2d396071-90de-444d-97c8-b0fd61b1348a','G4cKQ4XPZ5jbEhg8LvMTSXCYz85C0eiv','2017-09-05 19:14:36','','2017-09-05 19:14:36','',1,0,NULL,'','get','',NULL,NULL,0,NULL,'',0,0);
/*!40000 ALTER TABLE `fta_solutions_app_alarmapplication` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fta_solutions_app_alarmdef`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `fta_solutions_app_alarmdef` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `is_enabled` tinyint(1) NOT NULL,
  `is_deleted` tinyint(1) NOT NULL,
  `category` varchar(32) NOT NULL,
  `cc_biz_id` int(11) NOT NULL,
  `alarm_type` varchar(128) NOT NULL,
  `tnm_attr_id` longtext,
  `reg` varchar(255) DEFAULT NULL,
  `process` varchar(255) DEFAULT NULL,
  `module` longtext NOT NULL,
  `topo_set` longtext NOT NULL,
  `set_attr` longtext NOT NULL,
  `idc` longtext NOT NULL,
  `device_class` longtext NOT NULL,
  `responsible` varchar(255) DEFAULT NULL,
  `title` varchar(128) DEFAULT NULL,
  `description` longtext,
  `ok_notify` tinyint(1) NOT NULL,
  `notify` longtext NOT NULL,
  `solution_id` int(11) DEFAULT NULL,
  `timeout` int(11) NOT NULL,
  `source_type` varchar(32) DEFAULT NULL,
  `alarm_attr_id` varchar(128) DEFAULT NULL,
  `set_names` longtext NOT NULL,
  `module_names` longtext NOT NULL,
  `create_time` datetime NOT NULL,
  `create_user` varchar(32) NOT NULL,
  `update_time` datetime NOT NULL,
  `update_user` varchar(32) NOT NULL,
  `add_from` varchar(10) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fta_solutions_app_alarmdef_5b14b3ac` (`cc_biz_id`),
  KEY `fta_solutions_app_alarmdef_7a8d8e6e` (`solution_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fta_solutions_app_alarmdef`
--

LOCK TABLES `fta_solutions_app_alarmdef` WRITE;
/*!40000 ALTER TABLE `fta_solutions_app_alarmdef` DISABLE KEYS */;
/*!40000 ALTER TABLE `fta_solutions_app_alarmdef` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fta_solutions_app_alarminstance`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `fta_solutions_app_alarminstance` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `alarm_def_id` int(11) NOT NULL,
  `source_type` varchar(32) DEFAULT NULL,
  `source_id` varchar(255) DEFAULT NULL,
  `event_id` varchar(255) DEFAULT NULL,
  `ip` varchar(30) DEFAULT NULL,
  `raw` longtext NOT NULL,
  `status` varchar(30) DEFAULT NULL,
  `failure_type` varchar(30) DEFAULT NULL,
  `bpm_task_id` varchar(30) DEFAULT NULL,
  `comment` longtext,
  `source_time` datetime DEFAULT NULL,
  `finish_time` datetime DEFAULT NULL,
  `begin_time` datetime NOT NULL,
  `end_time` datetime DEFAULT NULL,
  `level` int(11) NOT NULL,
  `priority` int(11) NOT NULL,
  `cc_biz_id` int(11) NOT NULL,
  `alarm_type` varchar(128) NOT NULL,
  `solution_type` varchar(128) DEFAULT NULL,
  `snap_alarm_def` longtext,
  `snap_solution` longtext,
  `origin_alarm` longtext,
  `cc_topo_set` varchar(128) NOT NULL,
  `cc_app_module` varchar(128) NOT NULL,
  `inc_alarm_id` varchar(30) DEFAULT NULL,
  `uwork_id` varchar(30) DEFAULT NULL,
  `approved_time` datetime DEFAULT NULL,
  `approved_user` varchar(128) DEFAULT NULL,
  `approved_comment` varchar(128) DEFAULT NULL,
  `tnm_alarm` longtext,
  `tnm_alarm_id` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `event_id` (`event_id`),
  UNIQUE KEY `tnm_alarm_id` (`tnm_alarm_id`),
  KEY `fta_solutions_app_alarminstance_8e33d8d6` (`alarm_def_id`),
  KEY `fta_solutions_app_alarminstance_0afd9202` (`source_id`),
  KEY `fta_solutions_app_alarminstance_9acb4454` (`status`),
  KEY `fta_solutions_app_alarminstance_3820671b` (`source_time`),
  KEY `fta_solutions_app_alarminstance_c9e9a848` (`level`),
  KEY `fta_solutions_app_alarminstance_b988295c` (`priority`),
  KEY `fta_solutions_app_alarminstance_5b14b3ac` (`cc_biz_id`),
  KEY `fta_solutions_app_alarminstance_1e677533` (`alarm_type`),
  KEY `fta_solutions_app_alarminstance_69ff16fc` (`solution_type`),
  KEY `fta_solutions_app_alarminstance_6d0d989e` (`cc_topo_set`),
  KEY `fta_solutions_app_alarminstance_4173ccfa` (`cc_app_module`),
  KEY `fta_solutions_app_alarminstanc_source_type_7689371da94723f2_uniq` (`source_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fta_solutions_app_alarminstance`
--

LOCK TABLES `fta_solutions_app_alarminstance` WRITE;
/*!40000 ALTER TABLE `fta_solutions_app_alarminstance` DISABLE KEYS */;
/*!40000 ALTER TABLE `fta_solutions_app_alarminstance` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fta_solutions_app_alarminstancearchive`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `fta_solutions_app_alarminstancearchive` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date` date NOT NULL,
  `cc_biz_id` int(11) NOT NULL,
  `biz_team` varchar(128) NOT NULL,
  `is_success` tinyint(1) NOT NULL,
  `alarm_type` varchar(128) NOT NULL,
  `failure_type` varchar(32) DEFAULT NULL,
  `solution_type` varchar(32) DEFAULT NULL,
  `source_type` varchar(32) DEFAULT NULL,
  `is_off_time` tinyint(1) NOT NULL,
  `sub_count` int(10) unsigned NOT NULL,
  `sub_consumed` int(10) unsigned NOT NULL,
  `sub_profit` int(11) NOT NULL,
  `created_on` datetime NOT NULL,
  `updated_on` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `fta_solutions_app_alarminstancearchiv_date_78c35a10ad17e6e8_uniq` (`date`,`cc_biz_id`,`biz_team`,`is_success`,`alarm_type`,`failure_type`,`solution_type`,`source_type`,`is_off_time`),
  KEY `fta_solutions_app_alarminstancearchive_5fc73231` (`date`),
  KEY `fta_solutions_app_alarminstancearchive_5b14b3ac` (`cc_biz_id`),
  KEY `fta_solutions_app_alarminstancearchive_45ebbc43` (`biz_team`),
  KEY `fta_solutions_app_alarminstancearchive_1a4bfda4` (`is_success`),
  KEY `fta_solutions_app_alarminstancearchive_1e677533` (`alarm_type`),
  KEY `fta_solutions_app_alarminstancearchive_c9a77402` (`failure_type`),
  KEY `fta_solutions_app_alarminstancearchive_69ff16fc` (`solution_type`),
  KEY `fta_solutions_app_alarminstancearchive_08751261` (`source_type`),
  KEY `fta_solutions_app_alarminstancearchive_81e08331` (`is_off_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fta_solutions_app_alarminstancearchive`
--

LOCK TABLES `fta_solutions_app_alarminstancearchive` WRITE;
/*!40000 ALTER TABLE `fta_solutions_app_alarminstancearchive` DISABLE KEYS */;
/*!40000 ALTER TABLE `fta_solutions_app_alarminstancearchive` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fta_solutions_app_alarminstancebackup`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `fta_solutions_app_alarminstancebackup` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `alarm_def_id` int(11) NOT NULL,
  `source_type` varchar(32) DEFAULT NULL,
  `source_id` varchar(255) DEFAULT NULL,
  `event_id` varchar(255) DEFAULT NULL,
  `ip` varchar(30) DEFAULT NULL,
  `raw` longtext NOT NULL,
  `status` varchar(30) DEFAULT NULL,
  `failure_type` varchar(30) DEFAULT NULL,
  `bpm_task_id` varchar(30) DEFAULT NULL,
  `comment` longtext,
  `source_time` datetime DEFAULT NULL,
  `finish_time` datetime DEFAULT NULL,
  `begin_time` datetime NOT NULL,
  `end_time` datetime DEFAULT NULL,
  `level` int(11) NOT NULL,
  `priority` int(11) NOT NULL,
  `cc_biz_id` int(11) NOT NULL,
  `alarm_type` varchar(128) NOT NULL,
  `solution_type` varchar(128) DEFAULT NULL,
  `snap_alarm_def` longtext,
  `snap_solution` longtext,
  `origin_alarm` longtext,
  `cc_topo_set` varchar(128) NOT NULL,
  `cc_app_module` varchar(128) NOT NULL,
  `inc_alarm_id` varchar(30) DEFAULT NULL,
  `uwork_id` varchar(30) DEFAULT NULL,
  `approved_time` datetime DEFAULT NULL,
  `approved_user` varchar(128) DEFAULT NULL,
  `approved_comment` varchar(128) DEFAULT NULL,
  `tnm_alarm` longtext,
  `tnm_alarm_id` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `event_id` (`event_id`),
  UNIQUE KEY `tnm_alarm_id` (`tnm_alarm_id`),
  KEY `fta_solutions_app_alarminstancebackup_8e33d8d6` (`alarm_def_id`),
  KEY `fta_solutions_app_alarminstancebackup_0afd9202` (`source_id`),
  KEY `fta_solutions_app_alarminstancebackup_9acb4454` (`status`),
  KEY `fta_solutions_app_alarminstancebackup_3820671b` (`source_time`),
  KEY `fta_solutions_app_alarminstancebackup_c9e9a848` (`level`),
  KEY `fta_solutions_app_alarminstancebackup_b988295c` (`priority`),
  KEY `fta_solutions_app_alarminstancebackup_5b14b3ac` (`cc_biz_id`),
  KEY `fta_solutions_app_alarminstancebackup_1e677533` (`alarm_type`),
  KEY `fta_solutions_app_alarminstancebackup_69ff16fc` (`solution_type`),
  KEY `fta_solutions_app_alarminstancebackup_6d0d989e` (`cc_topo_set`),
  KEY `fta_solutions_app_alarminstancebackup_4173ccfa` (`cc_app_module`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fta_solutions_app_alarminstancebackup`
--

LOCK TABLES `fta_solutions_app_alarminstancebackup` WRITE;
/*!40000 ALTER TABLE `fta_solutions_app_alarminstancebackup` DISABLE KEYS */;
/*!40000 ALTER TABLE `fta_solutions_app_alarminstancebackup` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fta_solutions_app_alarminstancelog`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `fta_solutions_app_alarminstancelog` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `alarm_instance_id` int(11) NOT NULL,
  `content` longtext NOT NULL,
  `time` datetime NOT NULL,
  `step_name` varchar(32) DEFAULT NULL,
  `level` smallint(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fta_solutions_app_alarminstancelog_a211da11` (`alarm_instance_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fta_solutions_app_alarminstancelog`
--

LOCK TABLES `fta_solutions_app_alarminstancelog` WRITE;
/*!40000 ALTER TABLE `fta_solutions_app_alarminstancelog` DISABLE KEYS */;
/*!40000 ALTER TABLE `fta_solutions_app_alarminstancelog` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fta_solutions_app_alarmtype`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `fta_solutions_app_alarmtype` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cc_biz_id` int(11) NOT NULL,
  `is_enabled` tinyint(1) NOT NULL,
  `is_hidden` tinyint(1) NOT NULL,
  `source_type` varchar(128) NOT NULL,
  `alarm_type` varchar(128) NOT NULL,
  `pattern` varchar(128) NOT NULL,
  `description` longtext NOT NULL,
  `match_mode` int(11) NOT NULL,
  `exclude` longtext NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fta_solutions_app_alarmtype_5b14b3ac` (`cc_biz_id`),
  KEY `fta_solutions_app_alarmtype_08751261` (`source_type`),
  KEY `fta_solutions_app_alarmtype_1e677533` (`alarm_type`)
) ENGINE=InnoDB AUTO_INCREMENT=52 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fta_solutions_app_alarmtype`
--

LOCK TABLES `fta_solutions_app_alarmtype` WRITE;
/*!40000 ALTER TABLE `fta_solutions_app_alarmtype` DISABLE KEYS */;
INSERT INTO `fta_solutions_app_alarmtype` VALUES (1,0,1,0,'ALERT','cpu_3','cpu_3','5分钟平均负载（乘以100)',0,''),(2,0,1,0,'ALERT','cpu_7','cpu_7','cpu总使用率',0,''),(3,0,1,0,'ALERT','cpu_8','cpu_8','cpu单核使用率',0,''),(4,0,1,0,'ALERT','mem_98','mem_98','应用程序使用内存量',0,''),(5,0,1,0,'ALERT','mem_64','mem_64','物理内存使用率',0,''),(6,0,1,0,'ALERT','mem_97','mem_97','已用物理内存',0,''),(7,0,1,0,'ALERT','net_10','net_10','网卡入流量',0,''),(8,0,1,0,'ALERT','net_14','net_14','网卡出流量',0,''),(9,0,1,0,'ALERT','net_16','net_16','网卡发包量',0,''),(10,0,1,0,'ALERT','net_20','net_20','网卡收包量',0,''),(11,0,1,0,'ALERT','disk_81','disk_81','已用空间占比',0,''),(12,0,1,0,'ALERT','disk_86','disk_86','磁盘IO读速率',0,''),(13,0,1,0,'ALERT','disk_87','disk_87','磁盘IO写速率',0,''),(14,0,1,0,'ALERT','disk_96','disk_96','磁盘IO使用率',0,''),(15,0,1,0,'ALERT','BASE_ALARM_3','BASE_ALARM_3','磁盘只读',0,''),(16,0,1,0,'ALERT','BASE_ALARM_6','BASE_ALARM_6','磁盘写满',0,''),(17,0,1,0,'ALERT','BASE_ALARM_7','BASE_ALARM_7','Corefile产生',0,''),(18,0,1,0,'ALERT','custom','custom','自定义',0,''),(19,0,1,0,'ZABBIX','ZABBIX-agent.*','agent.*','Agent状态(agent.*)',2,''),(20,0,1,0,'ZABBIX','ZABBIX-system.cpu.*','system.cpu.*','CPU使用率(system.cpu.*)',2,''),(21,0,1,0,'ZABBIX','ZABBIX-vm.memory.size','vm.memory.size','内存使用量(vm.memory.size)',2,''),(22,0,1,0,'ZABBIX','ZABBIX-system.swap.*','system.swap.*','Swap使用量(system.swap.*)',2,''),(23,0,1,0,'ZABBIX','ZABBIX-kernel.*','kernel.*','系统内核状态(kernel.*)',2,''),(24,0,1,0,'ZABBIX','ZABBIX-vfs.dev.*','vfs.dev.*','磁盘IO使用率(vfs.dev.*)',2,''),(25,0,1,0,'ZABBIX','ZABBIX-vfs.fs.*','vfs.fs.*','磁盘容量(vfs.fs.*)',2,''),(26,0,1,0,'ZABBIX','ZABBIX-proc.num','proc.num','进程数量检查(proc.num)',2,''),(27,0,1,0,'ZABBIX','ZABBIX-icmpping*','icmpping*','Ping检查(icmpping*)',2,''),(28,0,1,0,'ZABBIX','ZABBIX-net.tcp.*','net.tcp.*','TCP链接检查(net.tcp.*)',2,''),(29,0,1,0,'ZABBIX','ZABBIX-net.udp.*','net.udp.*','UDP链接检查(net.udp.*)',2,''),(30,0,1,0,'ZABBIX','ZABBIX-vfs.file.*','vfs.file.*','文件状态检查(vfs.file.*)',2,''),(31,0,1,0,'ZABBIX','zabbix.*','zabbix.*','Zabbix其他',2,''),(32,0,1,0,'NAGIOS','NAGIOS-http','\\bhttp\\b','HTTP(http)',1,''),(33,0,1,0,'NAGIOS','NAGIOS-cpu','\\bcpu\\b','CPU(cpu)',1,''),(34,0,1,0,'NAGIOS','NAGIOS-memory','\\bmemory\\b','内存(memory)',1,''),(35,0,1,0,'NAGIOS','NAGIOS-net','\\bnet\\b','网络(net)',1,''),(36,0,1,0,'NAGIOS','NAGIOS-filesystem','\\bfilesystem\\b','文件系统(filesystem)',1,''),(37,0,1,0,'NAGIOS','NAGIOS-disk','\\bdisk\\b','磁盘(disk)',1,''),(38,0,1,0,'NAGIOS','NAGIOS-process','\\bprocess\\b','进程(process)',1,''),(39,0,1,0,'NAGIOS','NAGIOS-ping','\\bping\\b','Ping',1,''),(40,0,1,0,'NAGIOS','nagios','\\bnagios\\b','Nagios其他(nagios)',1,''),(41,0,1,0,'OPEN-FALCON','OPEN-FALCON-open-falcon-agent.*','agent.*','Agent状态(agent.*)',2,''),(42,0,1,0,'OPEN-FALCON','OPEN-FALCON-open-falcon-load.*','load.*','CPU使用率(load.*)',2,''),(43,0,1,0,'OPEN-FALCON','OPEN-FALCON-open-falcon-mem.*','mem.*','内存使用量(mem.*)',2,''),(44,0,1,0,'OPEN-FALCON','OPEN-FALCON-open-falcon-disk.io.*','disk.io.*','磁盘IO使用率(disk.io.*)',2,''),(45,0,1,0,'OPEN-FALCON','OPEN-FALCON-open-falcon-df.*','df.*','磁盘容量(df.*)',2,''),(46,0,1,0,'OPEN-FALCON','OPEN-FALCON-open-falcon-net.if.*','net.if.*','网卡流量(net.if.*)',2,''),(47,0,1,0,'OPEN-FALCON','OPEN-FALCON-open-falcon-net.port.listen','net.port.listen','端口监控(net.port.listen)',2,''),(48,0,1,0,'OPEN-FALCON','open-falcon.*','open-falcon.*','Open-falcon其他',2,''),(49,0,1,0,'REST-API','api_default','api_default','REST默认分类',0,''),(50,0,1,0,'FTA','fta_advice','fta_advice','预警自愈',2,''),(51,0,1,0,'CUSTOM','default','default','默认分类',0,'');
/*!40000 ALTER TABLE `fta_solutions_app_alarmtype` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fta_solutions_app_approvecallback`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `fta_solutions_app_approvecallback` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `obj_id` varchar(255) NOT NULL,
  `alarm_id` int(11) NOT NULL,
  `node_idx` int(11) NOT NULL,
  `approval` int(11) NOT NULL,
  `reason` varchar(255) DEFAULT NULL,
  `approver` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `obj_id` (`obj_id`),
  KEY `fta_solutions_app_approvecallback_b1f918f6` (`alarm_id`),
  KEY `fta_solutions_app_approvecallback_9ab7384e` (`node_idx`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fta_solutions_app_approvecallback`
--

LOCK TABLES `fta_solutions_app_approvecallback` WRITE;
/*!40000 ALTER TABLE `fta_solutions_app_approvecallback` DISABLE KEYS */;
/*!40000 ALTER TABLE `fta_solutions_app_approvecallback` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fta_solutions_app_bizconf`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `fta_solutions_app_bizconf` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cc_biz_id` int(11) NOT NULL,
  `responsible` varchar(512) DEFAULT NULL,
  `tnm_servicegroup_id` int(11) DEFAULT NULL,
  `online_data_source_host` char(15) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `cc_biz_id` (`cc_biz_id`),
  UNIQUE KEY `tnm_servicegroup_id` (`tnm_servicegroup_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fta_solutions_app_bizconf`
--

LOCK TABLES `fta_solutions_app_bizconf` WRITE;
/*!40000 ALTER TABLE `fta_solutions_app_bizconf` DISABLE KEYS */;
/*!40000 ALTER TABLE `fta_solutions_app_bizconf` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fta_solutions_app_conf`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `fta_solutions_app_conf` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `value` longtext NOT NULL,
  `description` longtext NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fta_solutions_app_conf`
--

LOCK TABLES `fta_solutions_app_conf` WRITE;
/*!40000 ALTER TABLE `fta_solutions_app_conf` DISABLE KEYS */;
INSERT INTO `fta_solutions_app_conf` VALUES (1,'FTA_ADMIN_LIST','admin','开发负责人，多个请以英文逗号(,)分隔'),(2,'WECHAT_APP_URL','http://paas-prod.bk.com/wechat/','APP微信端地址(外网可访问)'),(3,'WECHAT_STATIC_URL','http://paas-prod.bk.com/static/wechat/','APP微信端静态资源地址(外网可访问)'),(4,'WECHAT_SUPER_APPROVER','','微信审批的管理员，多个请以英文逗号(,)分隔'),(5,'WECHAT_TOKEN','','TOKEN'),(6,'WECHAT_ENCODING_AES_KEY','','EncodingAESKey'),(7,'WECHAT_CORPID','','微信企业号ID'),(8,'WECHAT_SECRET','','微信企业号Secret'),(9,'WECHAT_AGENT_ID','','发送消息的AGENT_ID'),(10,'WECHAT_API_TOKEN','bZ74Zke3KeKy','创建审批API_TOKEN');
/*!40000 ALTER TABLE `fta_solutions_app_conf` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fta_solutions_app_context`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `fta_solutions_app_context` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `key` varchar(128) NOT NULL,
  `field` varchar(128) NOT NULL,
  `value` longtext NOT NULL,
  `created_on` datetime DEFAULT NULL,
  `updated_on` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `fta_solutions_app_context_key_479774ab6f8ce62c_uniq` (`key`,`field`),
  KEY `fta_solutions_app_context_3c6e0b8a` (`key`),
  KEY `fta_solutions_app_context_c67f5cc7` (`updated_on`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fta_solutions_app_context`
--

LOCK TABLES `fta_solutions_app_context` WRITE;
/*!40000 ALTER TABLE `fta_solutions_app_context` DISABLE KEYS */;
/*!40000 ALTER TABLE `fta_solutions_app_context` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fta_solutions_app_datachanglog`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `fta_solutions_app_datachanglog` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `change_model` varchar(100) NOT NULL,
  `change_id` int(11) NOT NULL,
  `change_time` datetime NOT NULL,
  `change_type` varchar(20) NOT NULL,
  `new` longtext,
  `username` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=47 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fta_solutions_app_datachanglog`
--

LOCK TABLES `fta_solutions_app_datachanglog` WRITE;
/*!40000 ALTER TABLE `fta_solutions_app_datachanglog` DISABLE KEYS */;
INSERT INTO `fta_solutions_app_datachanglog` VALUES (1,'Conf',1,'2017-09-05 19:14:32','create','[{\"fields\": {\"name\": \"FTA_ADMIN_LIST\", \"value\": \"admin\", \"description\": \"开发负责人，多个请以英文逗号(,)分隔\"}, \"model\": \"fta_solutions_app.conf\", \"pk\": 1}]','*SYSTEM*'),(2,'IncidentDef',5,'2017-09-05 19:14:33','create','[{\"fields\": {\"is_enabled\": 1, \"description\": \"一系列单机异常类告警（同一起事件造成的多个告警）\", \"rule\": \"{\\n    \\\"alarm_type\\\": [\\n        \\\"ZABBIX-icmping*\\\",\\n        \\\"NAGIOS-ping\\\",\\n        \\\"BASE_ALARM_3\\\"\\n    ],\\n    \\\"timedelta\\\": 5,\\n    \\\"count\\\": 1,\\n    \\\"incident\\\": \\\"skip\\\",\\n    \\\"condition\\\": {\\n        \\\"alarm_type\\\": [\\n            \\\"ZABBIX-icmping*\\\",\\n            \\\"NAGIOS-ping\\\",\\n            \\\"BASE_ALARM_3\\\"\\n        ],\\n        \\\"host\\\": [\\n            \\\"self\\\"\\n        ]\\n    }\\n}\", \"priority\": 30, \"exclude\": \"\", \"codename\": \"ping_and_agent_time_out\", \"cc_biz_id\": 0}, \"model\": \"fta_solutions_app.incidentdef\", \"pk\": 5}]','*SYSTEM*'),(3,'IncidentDef',2,'2017-09-05 19:14:33','create','[{\"fields\": {\"is_enabled\": 1, \"description\": \"一系列处理套餐相同的告警（同一起事件造成的多个告警）\", \"rule\": \"{\\n    \\\"alarm_type\\\": [\\n        \\\"ZABBIX-icmping*\\\",\\n        \\\"NAGIOS-ping\\\",\\n        \\\"BASE_ALARM_3\\\"\\n    ],\\n    \\\"timedelta\\\": 5,\\n    \\\"count\\\": 1,\\n    \\\"incident\\\": \\\"skip\\\",\\n    \\\"condition\\\": {\\n        \\\"solution\\\": [\\n            \\\"self\\\"\\n        ],\\n        \\\"host\\\": [\\n            \\\"self\\\"\\n        ],\\n        \\\"alarm_type\\\": [\\n            \\\"ZABBIX-icmping*\\\",\\n            \\\"NAGIOS-ping\\\",\\n            \\\"BASE_ALARM_3\\\"\\n        ]\\n    }\\n}\", \"priority\": 50, \"exclude\": \"\", \"codename\": \"same_solution\", \"cc_biz_id\": 0}, \"model\": \"fta_solutions_app.incidentdef\", \"pk\": 2}]','*SYSTEM*'),(4,'Solution',4,'2017-09-05 19:14:33','create','[{\"fields\": {\"update_time\": \"2017-09-05T19:14:33.010\", \"update_user\": \"\", \"solution_type\": \"switch_ip\", \"title\": \"『快捷』后续处理对象故障机与备机互换\", \"creator\": \"管理员\", \"create_user\": \"\", \"create_time\": \"2017-09-05T19:14:33.010\", \"is_deleted\": false, \"codename\": \"diy_only\", \"config\": \" {}\", \"cc_biz_id\": 0}, \"model\": \"fta_solutions_app.solution\", \"pk\": 4}]','*SYSTEM*'),(5,'Solution',5,'2017-09-05 19:14:33','create','[{\"fields\": {\"update_time\": \"2017-09-05T19:14:33.016\", \"update_user\": \"\", \"solution_type\": \"bk_component\", \"title\": \"『快捷』CC拷贝故障机属性到备机\", \"creator\": \"管理员\", \"create_user\": \"\", \"create_time\": \"2017-09-05T19:14:33.015\", \"is_deleted\": false, \"codename\": \"diy_only\", \"config\": \"{\\\"module_name\\\":\\\"bk.cc\\\",\\\"task_name\\\":\\\"clone_host_property\\\",\\\"task_kwargs\\\":\\\"{\\\\n    \\\\\\\"uin\\\\\\\": \\\\\\\"100\\\\\\\",\\\\n    \\\\\\\"operator\\\\\\\": \\\\\\\"${operator}\\\\\\\",\\\\n \\\\\\\"app_id\\\\\\\": \\\\\\\"${cc_biz_id}\\\\\\\",\\\\n    \\\\\\\"plat_id\\\\\\\":\\\\\\\"${cc|plat_id}\\\\\\\",\\\\n    \\\\\\\"org_ip\\\\\\\":\\\\\\\"${bpm_context|alarm_ci_name}\\\\\\\" ,\\\\n    \\\\\\\"dst_ip\\\\\\\":\\\\\\\"${bpm_context|ip_bak}\\\\\\\"   \\\\n}\\\"}\", \"cc_biz_id\": 0}, \"model\": \"fta_solutions_app.solution\", \"pk\": 5}]','*SYSTEM*'),(6,'Solution',6,'2017-09-05 19:14:33','create','[{\"fields\": {\"update_time\": \"2017-09-05T19:14:33.019\", \"update_user\": \"\", \"solution_type\": \"bk_component\", \"title\": \"『快捷』CC移到“空闲机”模块\", \"creator\": \"管理员\", \"create_user\": \"\", \"create_time\": \"2017-09-05T19:14:33.019\", \"is_deleted\": false, \"codename\": \"diy_only\", \"config\": \"{\\\"module_name\\\":\\\"bk.cc\\\",\\\"task_name\\\":\\\"update_host_module\\\",\\\"task_kwargs\\\":\\\"{\\\\n    \\\\\\\"uin\\\\\\\": \\\\\\\"100\\\\\\\",\\\\n    \\\\\\\"operator\\\\\\\": \\\\\\\"${operator}\\\\\\\",\\\\n\\\\\\\"app_id\\\\\\\": \\\\\\\"${cc_biz_id}\\\\\\\", \\\\n    \\\\\\\"plat_id\\\\\\\": \\\\\\\"${cc|plat_id}\\\\\\\",\\\\n    \\\\\\\"dst_module_id\\\\\\\": \\\\\\\"${cc|idle_module_id}\\\\\\\",\\\\n    \\\\\\\"ip\\\\\\\": \\\\\\\"${ip}\\\\\\\"\\\\n}\\\"}\", \"cc_biz_id\": 0}, \"model\": \"fta_solutions_app.solution\", \"pk\": 6}]','*SYSTEM*'),(7,'Solution',7,'2017-09-05 19:14:33','create','[{\"fields\": {\"update_time\": \"2017-09-05T19:14:33.023\", \"update_user\": \"\", \"solution_type\": \"ijobs\", \"title\": \"『Non-Display』获取内存使用率TOP10的进程\", \"creator\": \"管理员\", \"create_user\": \"\", \"create_time\": \"2017-09-05T19:14:33.023\", \"is_deleted\": false, \"codename\": \"non-display\", \"config\": \"{\\\"app_id\\\":\\\"77770001\\\",\\\"task_id\\\":\\\"3\\\",\\\"ijobs_taski_name\\\":\\\"『快捷』获取内存使用率TOP10的进程\\\",\\\"parms\\\":\\\"\\\",\\\"parms0\\\":\\\"\\\",\\\"argv\\\":\\\"on\\\",\\\"retry_time\\\":\\\"10\\\",\\\"retry_count\\\":\\\"2\\\",\\\"steps\\\":\\\"1\\\",\\\"operator\\\":\\\"100\\\"}\", \"cc_biz_id\": 0}, \"model\": \"fta_solutions_app.solution\", \"pk\": 7}]','*SYSTEM*'),(8,'Solution',8,'2017-09-05 19:14:33','create','[{\"fields\": {\"update_time\": \"2017-09-05T19:14:33.026\", \"update_user\": \"\", \"solution_type\": \"ijobs\", \"title\": \"『Non-Display』获取CPU使用率TOP10的进程\", \"creator\": \"管理员\", \"create_user\": \"\", \"create_time\": \"2017-09-05T19:14:33.026\", \"is_deleted\": false, \"codename\": \"non-display\", \"config\": \"{\\\"app_id\\\":\\\"77770001\\\",\\\"task_id\\\":\\\"2\\\",\\\"ijobs_taski_name\\\":\\\"『快捷』获取CPU使用率TOP10的进程\\\",\\\"parms\\\":\\\"\\\",\\\"parms0\\\":\\\"\\\",\\\"argv\\\":\\\"on\\\",\\\"retry_time\\\":\\\"10\\\",\\\"retry_count\\\":\\\"2\\\",\\\"steps\\\":\\\"1\\\",\\\"operator\\\":\\\"100\\\"}\", \"cc_biz_id\": 0}, \"model\": \"fta_solutions_app.solution\", \"pk\": 8}]','*SYSTEM*'),(9,'Solution',9,'2017-09-05 19:14:33','create','[{\"fields\": {\"update_time\": \"2017-09-05T19:14:33.029\", \"update_user\": \"\", \"solution_type\": \"notice\", \"title\": \"『Non-Display』发送CPU使用率TOP10的进程(微信)\", \"creator\": \"管理员\", \"create_user\": \"\", \"create_time\": \"2017-09-05T19:14:33.029\", \"is_deleted\": false, \"codename\": \"non-display\", \"config\": \"{\\\"message\\\":\\\"【故障自愈】CPU使用率TOP10列表：\\\\n业务：\\\\\\\"${cc|ApplicationName}\\\\\\\"\\\\n模块：\\\\\\\"${cc|ModuleName}\\\\\\\"\\\\n主机：${ip}\\\\n---------------------------------------\\\\n${bpm_context|ijobs_return_cpu}\\\",\\\"extra_people\\\":\\\"\\\",\\\"extra_people_select\\\":null,\\\"wechat\\\":\\\"on\\\"}\", \"cc_biz_id\": 0}, \"model\": \"fta_solutions_app.solution\", \"pk\": 9}]','*SYSTEM*'),(10,'Solution',10,'2017-09-05 19:14:33','create','[{\"fields\": {\"update_time\": \"2017-09-05T19:14:33.032\", \"update_user\": \"\", \"solution_type\": \"graph\", \"title\": \"『快捷』发送CPU使用率TOP10的进程(微信)\", \"creator\": \"管理员\", \"create_user\": \"\", \"create_time\": \"2017-09-05T19:14:33.032\", \"is_deleted\": false, \"codename\": \"cpu_proc_top10\", \"config\": \"{\\\"real_solutions\\\":\\\"[[{\\\\\\\"1\\\\\\\": [\\\\\\\"success\\\\\\\"]}, \\\\\\\"8\\\\\\\"], [{}, \\\\\\\"9\\\\\\\"]]\\\"}\", \"cc_biz_id\": 0}, \"model\": \"fta_solutions_app.solution\", \"pk\": 10}]','*SYSTEM*'),(11,'Solution',24,'2017-09-05 19:14:33','create','[{\"fields\": {\"update_time\": \"2017-09-05T19:14:33.035\", \"update_user\": \"\", \"solution_type\": \"notice\", \"title\": \"『Non-Display』发送内存使用率TOP10的进程(微信)\", \"creator\": \"管理员\", \"create_user\": \"\", \"create_time\": \"2017-09-05T19:14:33.035\", \"is_deleted\": false, \"codename\": \"non-display\", \"config\": \"{\\\"message\\\":\\\"【故障自愈】内存使用率TOP10列表：\\\\n业务：\\\\\\\"${cc|ApplicationName}\\\\\\\"\\\\n模块：\\\\\\\"${cc|ModuleName}\\\\\\\"\\\\n主机：${ip}\\\\n---------------------------------------\\\\n${bpm_context|ijobs_return_mem}\\\",\\\"extra_people\\\":\\\"\\\",\\\"extra_people_select\\\":null,\\\"wechat\\\":\\\"on\\\"}\", \"cc_biz_id\": 0}, \"model\": \"fta_solutions_app.solution\", \"pk\": 24}]','*SYSTEM*'),(12,'Solution',25,'2017-09-05 19:14:33','create','[{\"fields\": {\"update_time\": \"2017-09-05T19:14:33.037\", \"update_user\": \"\", \"solution_type\": \"graph\", \"title\": \"『快捷』发送内存使用率TOP10的进程(微信)\", \"creator\": \"管理员\", \"create_user\": \"\", \"create_time\": \"2017-09-05T19:14:33.037\", \"is_deleted\": false, \"codename\": \"mem_proc_top10\", \"config\": \"{\\\"real_solutions\\\":\\\"[[{\\\\\\\"1\\\\\\\": [\\\\\\\"success\\\\\\\"]}, \\\\\\\"7\\\\\\\"], [{}, \\\\\\\"24\\\\\\\"]]\\\"}\", \"cc_biz_id\": 0}, \"model\": \"fta_solutions_app.solution\", \"pk\": 25}]','*SYSTEM*'),(13,'Solution',36,'2017-09-05 19:14:33','create','[{\"fields\": {\"update_time\": \"2017-09-05T19:14:33.040\", \"update_user\": \"\", \"solution_type\": \"bk_component\", \"title\": \"『快捷』CC移到“故障机”模块\", \"creator\": \"管理员\", \"create_user\": \"\", \"create_time\": \"2017-09-05T19:14:33.040\", \"is_deleted\": false, \"codename\": \"cc_to_fault_module\", \"config\": \"{\\\"module_name\\\":\\\"bk.cc\\\",\\\"task_name\\\":\\\"update_host_module\\\",\\\"task_kwargs\\\":\\\"{\\\\n    \\\\\\\"uin\\\\\\\": \\\\\\\"100\\\\\\\",\\\\n    \\\\\\\"operator\\\\\\\": \\\\\\\"${operator}\\\\\\\",\\\\n\\\\\\\"app_id\\\\\\\": \\\\\\\"${cc_biz_id}\\\\\\\", \\\\n    \\\\\\\"plat_id\\\\\\\": \\\\\\\"${cc|plat_id}\\\\\\\",\\\\n    \\\\\\\"dst_module_id\\\\\\\": \\\\\\\"${cc|fault_module_id}\\\\\\\",\\\\n    \\\\\\\"ip\\\\\\\": \\\\\\\"${ip}\\\\\\\" \\\\n}\\\"}\", \"cc_biz_id\": 0}, \"model\": \"fta_solutions_app.solution\", \"pk\": 36}]','*SYSTEM*'),(14,'Solution',37,'2017-09-05 19:14:33','create','[{\"fields\": {\"update_time\": \"2017-09-05T19:14:33.043\", \"update_user\": \"\", \"solution_type\": \"notice\", \"title\": \"『Non-Display』发送CPU使用率TOP10的进程(短信)\", \"creator\": \"管理员\", \"create_user\": \"\", \"create_time\": \"2017-09-05T19:14:33.043\", \"is_deleted\": false, \"codename\": \"non-display\", \"config\": \"{\\\"message\\\":\\\"【故障自愈】CPU使用率TOP10列表：\\\\n业务：\\\\\\\"${cc|ApplicationName}\\\\\\\"\\\\n模块：\\\\\\\"${cc|ModuleName}\\\\\\\"\\\\n主机：${ip}\\\\n---------------------------------------\\\\n${bpm_context|ijobs_return_cpu}\\\",\\\"extra_people\\\":\\\"\\\",\\\"extra_people_select\\\":null,\\\"sms\\\":\\\"on\\\"}\", \"cc_biz_id\": 0}, \"model\": \"fta_solutions_app.solution\", \"pk\": 37}]','*SYSTEM*'),(15,'Solution',38,'2017-09-05 19:14:33','create','[{\"fields\": {\"update_time\": \"2017-09-05T19:14:33.046\", \"update_user\": \"\", \"solution_type\": \"notice\", \"title\": \"『Non-Display』发送CPU使用率TOP10的进程(邮件)\", \"creator\": \"管理员\", \"create_user\": \"\", \"create_time\": \"2017-09-05T19:14:33.046\", \"is_deleted\": false, \"codename\": \"non-display\", \"config\": \"{\\\"message\\\":\\\"【故障自愈】CPU使用率TOP10列表：\\\\n业务：\\\\\\\"${cc|ApplicationName}\\\\\\\"\\\\n模块：\\\\\\\"${cc|ModuleName}\\\\\\\"\\\\n主机：${ip}\\\\n---------------------------------------\\\\n${bpm_context|ijobs_return_cpu}\\\",\\\"extra_people\\\":\\\"\\\",\\\"extra_people_select\\\":null,\\\"email\\\":\\\"on\\\"}\", \"cc_biz_id\": 0}, \"model\": \"fta_solutions_app.solution\", \"pk\": 38}]','*SYSTEM*'),(16,'Solution',39,'2017-09-05 19:14:33','create','[{\"fields\": {\"update_time\": \"2017-09-05T19:14:33.049\", \"update_user\": \"\", \"solution_type\": \"notice\", \"title\": \"『Non-Display』发送内存使用率TOP10的进程(短信)\", \"creator\": \"管理员\", \"create_user\": \"\", \"create_time\": \"2017-09-05T19:14:33.049\", \"is_deleted\": false, \"codename\": \"non-display\", \"config\": \"{\\\"message\\\":\\\"【故障自愈】内存使用率TOP10列表：\\\\n业务：\\\\\\\"${cc|ApplicationName}\\\\\\\"\\\\n模块：\\\\\\\"${cc|ModuleName}\\\\\\\"\\\\n主机：${ip}\\\\n---------------------------------------\\\\n${bpm_context|ijobs_return_mem}\\\",\\\"extra_people\\\":\\\"\\\",\\\"extra_people_select\\\":null,\\\"sms\\\":\\\"on\\\"}\", \"cc_biz_id\": 0}, \"model\": \"fta_solutions_app.solution\", \"pk\": 39}]','*SYSTEM*'),(17,'Solution',40,'2017-09-05 19:14:33','create','[{\"fields\": {\"update_time\": \"2017-09-05T19:14:33.051\", \"update_user\": \"\", \"solution_type\": \"notice\", \"title\": \"『Non-Display』发送内存使用率TOP10的进程(邮件)\", \"creator\": \"管理员\", \"create_user\": \"\", \"create_time\": \"2017-09-05T19:14:33.051\", \"is_deleted\": false, \"codename\": \"non-display\", \"config\": \"{\\\"message\\\":\\\"【故障自愈】内存使用率TOP10列表：\\\\n业务：\\\\\\\"${cc|ApplicationName}\\\\\\\"\\\\n模块：\\\\\\\"${cc|ModuleName}\\\\\\\"\\\\n主机：${ip}\\\\n---------------------------------------\\\\n${bpm_context|ijobs_return_mem}\\\",\\\"extra_people\\\":\\\"\\\",\\\"extra_people_select\\\":null,\\\"email\\\":\\\"on\\\"}\", \"cc_biz_id\": 0}, \"model\": \"fta_solutions_app.solution\", \"pk\": 40}]','*SYSTEM*'),(18,'AdviceDef',1,'2017-09-05 19:14:33','create','[{\"fields\": {\"is_enabled\": 1, \"subject_type\": \"host\", \"check_sub_type\": \"ZABBIX-icmping*\", \"check_type\": \"alarm\", \"advice\": \"确认主机是否存在硬件故障，需要做下线或者替换操作\", \"interval\": 7, \"advice_type\": \"hardware\", \"create_time\": \"2017-09-05T19:14:33.060\", \"threshold\": 3, \"codename\": \"host-down-weekly\", \"cc_biz_id\": 0, \"description\": \"7天内|同一主机|产生3+条严重告警，应产生硬件待优化事件进行后续跟踪。\"}, \"model\": \"fta_solutions_app.advicedef\", \"pk\": 1}]','*SYSTEM*'),(19,'AdviceDef',2,'2017-09-05 19:14:33','create','[{\"fields\": {\"is_enabled\": 1, \"subject_type\": \"host\", \"check_sub_type\": \"NAGIOS-ping\", \"check_type\": \"alarm\", \"advice\": \"确认主机是否存在硬件故障，需要做下线或者替换操作\", \"interval\": 7, \"advice_type\": \"hardware\", \"create_time\": \"2017-09-05T19:14:33.061\", \"threshold\": 3, \"codename\": \"host-down-weekly\", \"cc_biz_id\": 0, \"description\": \"7天内|同一主机|产生3+条严重告警，应产生硬件待优化事件进行后续跟踪。\"}, \"model\": \"fta_solutions_app.advicedef\", \"pk\": 2}]','*SYSTEM*'),(20,'AdviceDef',3,'2017-09-05 19:14:33','create','[{\"fields\": {\"is_enabled\": 1, \"subject_type\": \"host\", \"check_sub_type\": \"BASE_ALARM_3\", \"check_type\": \"alarm\", \"advice\": \"提单请现场确认主机硬件是否故障\", \"interval\": 7, \"advice_type\": \"hardware\", \"create_time\": \"2017-09-05T19:14:33.062\", \"threshold\": 3, \"codename\": \"disk-readonly-weekly\", \"cc_biz_id\": 0, \"description\": \"7天内|同一主机|产生3+条硬盘只读告警，应产生硬件待优化事件进行人工确认。\"}, \"model\": \"fta_solutions_app.advicedef\", \"pk\": 3}]','*SYSTEM*'),(21,'AdviceDef',4,'2017-09-05 19:14:33','create','[{\"fields\": {\"is_enabled\": 1, \"subject_type\": \"host\", \"check_sub_type\": \"OPEN-FALCON-open-falcon-df.*\", \"check_type\": \"alarm\", \"advice\": \"1、请检查当前的磁盘清理策略确实是否需要调整\\n2、确认该模块当前机型的硬盘空间是否合理\", \"interval\": 7, \"advice_type\": \"ops\", \"create_time\": \"2017-09-05T19:14:33.063\", \"threshold\": 3, \"codename\": \"disk-full-weekly\", \"cc_biz_id\": 0, \"description\": \"7天内|同一主机|产生3+条磁盘满告警，应产生运维待优化事件进行后续跟踪。\"}, \"model\": \"fta_solutions_app.advicedef\", \"pk\": 4}]','*SYSTEM*'),(22,'AdviceDef',5,'2017-09-05 19:14:33','create','[{\"fields\": {\"is_enabled\": 1, \"subject_type\": \"host\", \"check_sub_type\": \"ZABBIX-vfs.fs.*\", \"check_type\": \"alarm\", \"advice\": \"1、请检查当前的磁盘清理策略确实是否需要调整\\n2、确认该模块当前机型的硬盘空间是否合理\", \"interval\": 7, \"advice_type\": \"ops\", \"create_time\": \"2017-09-05T19:14:33.064\", \"threshold\": 3, \"codename\": \"disk-full-weekly\", \"cc_biz_id\": 0, \"description\": \"7天内|同一主机|产生3+条磁盘满告警，应产生运维待优化事件进行后续跟踪。\"}, \"model\": \"fta_solutions_app.advicedef\", \"pk\": 5}]','*SYSTEM*'),(23,'AdviceDef',6,'2017-09-05 19:14:33','create','[{\"fields\": {\"is_enabled\": 1, \"subject_type\": \"host\", \"check_sub_type\": \"BASE_ALARM_6\", \"check_type\": \"alarm\", \"advice\": \"1、请检查当前的磁盘清理策略确实是否需要调整\\n2、确认该模块当前机型的硬盘空间是否合理\", \"interval\": 7, \"advice_type\": \"ops\", \"create_time\": \"2017-09-05T19:14:33.065\", \"threshold\": 3, \"codename\": \"disk-full-weekly\", \"cc_biz_id\": 0, \"description\": \"7天内|同一主机|产生3+条磁盘满告警，应产生运维待优化事件进行后续跟踪。\"}, \"model\": \"fta_solutions_app.advicedef\", \"pk\": 6}]','*SYSTEM*'),(24,'AdviceDef',7,'2017-09-05 19:14:33','create','[{\"fields\": {\"is_enabled\": 1, \"subject_type\": \"host\", \"check_sub_type\": \"OPEN-FALCON-open-falcon-df.*\", \"check_type\": \"alarm\", \"advice\": \"1、请检查当前的磁盘清理策略确实是否需要调整\\n2、确认该模块当前机型的硬盘空间是否合理\", \"interval\": 30, \"advice_type\": \"ops\", \"create_time\": \"2017-09-05T19:14:33.066\", \"threshold\": 5, \"codename\": \"disk-full-monthly\", \"cc_biz_id\": 0, \"description\": \"30天内|同一主机|产生5+条磁盘满告警，应产生运维待优化事件进行后续跟踪。\"}, \"model\": \"fta_solutions_app.advicedef\", \"pk\": 7}]','*SYSTEM*'),(25,'AdviceDef',8,'2017-09-05 19:14:33','create','[{\"fields\": {\"is_enabled\": 1, \"subject_type\": \"host\", \"check_sub_type\": \"ZABBIX-vfs.fs.*\", \"check_type\": \"alarm\", \"advice\": \"1、请检查当前的磁盘清理策略确实是否需要调整\\n2、确认该模块当前机型的硬盘空间是否合理\", \"interval\": 30, \"advice_type\": \"ops\", \"create_time\": \"2017-09-05T19:14:33.067\", \"threshold\": 5, \"codename\": \"disk-full-monthly\", \"cc_biz_id\": 0, \"description\": \"30天内|同一主机|产生5+条磁盘满告警，应产生运维待优化事件进行后续跟踪。\"}, \"model\": \"fta_solutions_app.advicedef\", \"pk\": 8}]','*SYSTEM*'),(26,'AdviceDef',9,'2017-09-05 19:14:33','create','[{\"fields\": {\"is_enabled\": 1, \"subject_type\": \"host\", \"check_sub_type\": \"BASE_ALARM_6\", \"check_type\": \"alarm\", \"advice\": \"1、请检查当前的磁盘清理策略确实是否需要调整\\n2、确认该模块当前机型的硬盘空间是否合理\", \"interval\": 30, \"advice_type\": \"ops\", \"create_time\": \"2017-09-05T19:14:33.068\", \"threshold\": 5, \"codename\": \"disk-full-monthly\", \"cc_biz_id\": 0, \"description\": \"30天内|同一主机|产生5+条磁盘满告警，应产生运维待优化事件进行后续跟踪。\"}, \"model\": \"fta_solutions_app.advicedef\", \"pk\": 9}]','*SYSTEM*'),(27,'AdviceDef',10,'2017-09-05 19:14:33','create','[{\"fields\": {\"is_enabled\": 1, \"subject_type\": \"host\", \"check_sub_type\": \"OPEN-FALCON-open-falcon-df.*\", \"check_type\": \"alarm\", \"advice\": \"1、请检查当前的磁盘清理策略确实是否需要调整\\n2、确认该模块当前机型的硬盘空间是否合理\", \"interval\": 1, \"advice_type\": \"ops\", \"create_time\": \"2017-09-05T19:14:33.069\", \"threshold\": 2, \"codename\": \"disk-full-daily\", \"cc_biz_id\": 0, \"description\": \"1天内|同一主机|产生2+条磁盘满告警，应产生运维待优化事件进行后续跟踪。\"}, \"model\": \"fta_solutions_app.advicedef\", \"pk\": 10}]','*SYSTEM*'),(28,'AdviceDef',11,'2017-09-05 19:14:33','create','[{\"fields\": {\"is_enabled\": 1, \"subject_type\": \"host\", \"check_sub_type\": \"ZABBIX-vfs.fs.*\", \"check_type\": \"alarm\", \"advice\": \"1、请检查当前的磁盘清理策略确实是否需要调整\\n2、确认该模块当前机型的硬盘空间是否合理\", \"interval\": 1, \"advice_type\": \"ops\", \"create_time\": \"2017-09-05T19:14:33.070\", \"threshold\": 2, \"codename\": \"disk-full-daily\", \"cc_biz_id\": 0, \"description\": \"1天内|同一主机|产生2+条磁盘满告警，应产生运维待优化事件进行后续跟踪。\"}, \"model\": \"fta_solutions_app.advicedef\", \"pk\": 11}]','*SYSTEM*'),(29,'AdviceDef',12,'2017-09-05 19:14:33','create','[{\"fields\": {\"is_enabled\": 1, \"subject_type\": \"host\", \"check_sub_type\": \"BASE_ALARM_6\", \"check_type\": \"alarm\", \"advice\": \"1、请检查当前的磁盘清理策略确实是否需要调整\\n2、确认该模块当前机型的硬盘空间是否合理\", \"interval\": 1, \"advice_type\": \"ops\", \"create_time\": \"2017-09-05T19:14:33.071\", \"threshold\": 2, \"codename\": \"disk-full-daily\", \"cc_biz_id\": 0, \"description\": \"1天内|同一主机|产生2+条磁盘满告警，应产生运维待优化事件进行后续跟踪。\"}, \"model\": \"fta_solutions_app.advicedef\", \"pk\": 12}]','*SYSTEM*'),(30,'AdviceDef',13,'2017-09-05 19:14:33','create','[{\"fields\": {\"is_enabled\": 1, \"subject_type\": \"host\", \"check_sub_type\": \"BASE_ALARM_3\", \"check_type\": \"alarm\", \"advice\": \"提单请现场确认主机硬件是否故障\", \"interval\": 30, \"advice_type\": \"hardware\", \"create_time\": \"2017-09-05T19:14:33.072\", \"threshold\": 3, \"codename\": \"disk-readonly-monthly\", \"cc_biz_id\": 0, \"description\": \"30天内|同一主机|产生3+条硬盘只读告警，应产生硬件待优化事件进行后续跟踪。\"}, \"model\": \"fta_solutions_app.advicedef\", \"pk\": 13}]','*SYSTEM*'),(31,'AdviceDef',14,'2017-09-05 19:14:33','create','[{\"fields\": {\"is_enabled\": 1, \"subject_type\": \"host\", \"check_sub_type\": \"BASE_ALARM_3\", \"check_type\": \"alarm\", \"advice\": \"提单请现场确认主机硬件是否故障\", \"interval\": 1, \"advice_type\": \"hardware\", \"create_time\": \"2017-09-05T19:14:33.074\", \"threshold\": 2, \"codename\": \"disk-readonly-daily\", \"cc_biz_id\": 0, \"description\": \"1天内|同一主机|产生2+条硬盘只读告警，应产生硬件待优化事件进行人工确认。\"}, \"model\": \"fta_solutions_app.advicedef\", \"pk\": 14}]','*SYSTEM*'),(32,'AdviceDef',15,'2017-09-05 19:14:33','create','[{\"fields\": {\"is_enabled\": 1, \"subject_type\": \"host\", \"check_sub_type\": \"ZABBIX-icmping*\", \"check_type\": \"alarm\", \"advice\": \"确认主机是否存在硬件故障，需要做下线或者替换操作\", \"interval\": 1, \"advice_type\": \"hardware\", \"create_time\": \"2017-09-05T19:14:33.075\", \"threshold\": 2, \"codename\": \"host-down-daily\", \"cc_biz_id\": 0, \"description\": \"1天内|同一主机|产生2+条严重告警，应产生硬件待优化事件进行后续跟踪。\"}, \"model\": \"fta_solutions_app.advicedef\", \"pk\": 15}]','*SYSTEM*'),(33,'AdviceDef',16,'2017-09-05 19:14:33','create','[{\"fields\": {\"is_enabled\": 1, \"subject_type\": \"host\", \"check_sub_type\": \"NAGIOS-ping\", \"check_type\": \"alarm\", \"advice\": \"确认主机是否存在硬件故障，需要做下线或者替换操作\", \"interval\": 1, \"advice_type\": \"hardware\", \"create_time\": \"2017-09-05T19:14:33.076\", \"threshold\": 2, \"codename\": \"host-down-daily\", \"cc_biz_id\": 0, \"description\": \"1天内|同一主机|产生2+条严重告警，应产生硬件待优化事件进行后续跟踪。\"}, \"model\": \"fta_solutions_app.advicedef\", \"pk\": 16}]','*SYSTEM*'),(34,'AdviceDef',17,'2017-09-05 19:14:33','create','[{\"fields\": {\"is_enabled\": 1, \"subject_type\": \"host\", \"check_sub_type\": \"ZABBIX-icmping*\", \"check_type\": \"alarm\", \"advice\": \"确认主机是否存在硬件故障，需要做下线或者替换操作\", \"interval\": 30, \"advice_type\": \"hardware\", \"create_time\": \"2017-09-05T19:14:33.077\", \"threshold\": 5, \"codename\": \"host-down-monthly\", \"cc_biz_id\": 0, \"description\": \"30天内|同一主机|产生5+条严重告警，应产生硬件待优化事件进行后续跟踪。\"}, \"model\": \"fta_solutions_app.advicedef\", \"pk\": 17}]','*SYSTEM*'),(35,'AdviceDef',18,'2017-09-05 19:14:33','create','[{\"fields\": {\"is_enabled\": 1, \"subject_type\": \"host\", \"check_sub_type\": \"NAGIOS-ping\", \"check_type\": \"alarm\", \"advice\": \"确认主机是否存在硬件故障，需要做下线或者替换操作\", \"interval\": 30, \"advice_type\": \"hardware\", \"create_time\": \"2017-09-05T19:14:33.078\", \"threshold\": 5, \"codename\": \"host-down-monthly\", \"cc_biz_id\": 0, \"description\": \"30天内|同一主机|产生5+条严重告警，应产生硬件待优化事件进行后续跟踪。\"}, \"model\": \"fta_solutions_app.advicedef\", \"pk\": 18}]','*SYSTEM*'),(36,'Conf',2,'2017-09-05 19:14:33','create','[{\"fields\": {\"name\": \"WECHAT_APP_URL\", \"value\": \"http://paas-prod.bk.com/wechat/\", \"description\": \"APP微信端地址(外网可访问)\"}, \"model\": \"fta_solutions_app.conf\", \"pk\": 2}]','*SYSTEM*'),(37,'Conf',3,'2017-09-05 19:14:33','create','[{\"fields\": {\"name\": \"WECHAT_STATIC_URL\", \"value\": \"http://paas-prod.bk.com/static/wechat/\", \"description\": \"APP微信端静态资源地址(外网可访问)\"}, \"model\": \"fta_solutions_app.conf\", \"pk\": 3}]','*SYSTEM*'),(38,'Conf',4,'2017-09-05 19:14:33','create','[{\"fields\": {\"name\": \"WECHAT_SUPER_APPROVER\", \"value\": \"\", \"description\": \"微信审批的管理员，多个请以英文逗号(,)分隔\"}, \"model\": \"fta_solutions_app.conf\", \"pk\": 4}]','*SYSTEM*'),(39,'Conf',5,'2017-09-05 19:14:33','create','[{\"fields\": {\"name\": \"WECHAT_TOKEN\", \"value\": \"\", \"description\": \"TOKEN\"}, \"model\": \"fta_solutions_app.conf\", \"pk\": 5}]','*SYSTEM*'),(40,'Conf',6,'2017-09-05 19:14:33','create','[{\"fields\": {\"name\": \"WECHAT_ENCODING_AES_KEY\", \"value\": \"\", \"description\": \"EncodingAESKey\"}, \"model\": \"fta_solutions_app.conf\", \"pk\": 6}]','*SYSTEM*'),(41,'Conf',7,'2017-09-05 19:14:33','create','[{\"fields\": {\"name\": \"WECHAT_CORPID\", \"value\": \"\", \"description\": \"微信企业号ID\"}, \"model\": \"fta_solutions_app.conf\", \"pk\": 7}]','*SYSTEM*'),(42,'Conf',8,'2017-09-05 19:14:33','create','[{\"fields\": {\"name\": \"WECHAT_SECRET\", \"value\": \"\", \"description\": \"微信企业号Secret\"}, \"model\": \"fta_solutions_app.conf\", \"pk\": 8}]','*SYSTEM*'),(43,'Conf',9,'2017-09-05 19:14:33','create','[{\"fields\": {\"name\": \"WECHAT_AGENT_ID\", \"value\": \"\", \"description\": \"发送消息的AGENT_ID\"}, \"model\": \"fta_solutions_app.conf\", \"pk\": 9}]','*SYSTEM*'),(44,'Conf',10,'2017-09-05 19:14:33','create','[{\"fields\": {\"name\": \"WECHAT_API_TOKEN\", \"value\": \"bZ74Zke3KeKy\", \"description\": \"创建审批API_TOKEN\"}, \"model\": \"fta_solutions_app.conf\", \"pk\": 10}]','*SYSTEM*'),(45,'AdviceFtaDef',1,'2017-09-05 19:14:35','create','[{\"fields\": {\"is_enabled\": 1, \"is_deleted\": false, \"description\": \"内置策略\", \"title\": null, \"module_names\": \"空闲机\", \"responsible\": null, \"cc_biz_id\": 0, \"module\": \"\", \"advice_def_id\": 17, \"notify\": \"{\\n        \\\"begin_notify_wechat\\\":true,\\n        \\\"begin_notify_mail\\\":true,\\n        \\\"begin_notify_sms\\\":false,\\n        \\\"begin_notify_im\\\":false,\\n        \\\"begin_notify_phone\\\":false,\\n        \\\"success_notify_wechat\\\":true,\\n        \\\"success_notify_mail\\\":true,\\n        \\\"success_notify_sms\\\":false,\\n        \\\"success_notify_im\\\":false,\\n        \\\"success_notify_phone\\\":false,\\n        \\\"failure_notify_wechat\\\":true,\\n        \\\"failure_notify_mail\\\":true,\\n        \\\"failure_notify_sms\\\":false,\\n        \\\"failure_notify_im\\\":false,\\n        \\\"failure_notify_phone\\\":false,\\n        \\\"to_extra\\\":false,\\n        \\\"to_role\\\":true\\n    }\", \"timeout\": 40, \"exclude\": \"\", \"solution_id\": 36, \"set_names\": \"\", \"handle_type\": \"solution\", \"topo_set\": \"\"}, \"model\": \"fta_solutions_app.adviceftadef\", \"pk\": 1}]','*SYSTEM*'),(46,'AlarmApplication',1,'2017-09-05 19:14:36','create','[{\"fields\": {\"exception_data\": \"\", \"activate_time\": null, \"update_user\": \"\", \"app_name\": \"蓝鲸监控的告警源\", \"extra\": null, \"app_secret\": \"G4cKQ4XPZ5jbEhg8LvMTSXCYz85C0eiv\", \"app_id\": \"2d396071-90de-444d-97c8-b0fd61b1348a\", \"create_user\": \"\", \"create_time\": \"2017-09-05T19:14:36.078\", \"exclude\": \"\", \"app_url\": \"\", \"exception_begin_time\": null, \"empty_num\": 0, \"cc_biz_id\": 0, \"is_enabled\": true, \"update_time\": \"2017-09-05T19:14:36.078\", \"app_method\": \"get\", \"source_type\": \"ALERT\", \"exception_num\": 0, \"is_deleted\": false, \"empty_begin_time\": null, \"exception_max_num\": 0}, \"model\": \"fta_solutions_app.alarmapplication\", \"pk\": 1}]','*SYSTEM*');
/*!40000 ALTER TABLE `fta_solutions_app_datachanglog` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fta_solutions_app_eagleeye`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `fta_solutions_app_eagleeye` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `incident_id` int(11) NOT NULL,
  `eagle_eye_orderno` varchar(128) NOT NULL,
  `data_type` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fta_solutions_app_eagleeye_f5ce6141` (`incident_id`),
  KEY `fta_solutions_app_eagleeye_0dfdbdbf` (`eagle_eye_orderno`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fta_solutions_app_eagleeye`
--

LOCK TABLES `fta_solutions_app_eagleeye` WRITE;
/*!40000 ALTER TABLE `fta_solutions_app_eagleeye` DISABLE KEYS */;
/*!40000 ALTER TABLE `fta_solutions_app_eagleeye` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fta_solutions_app_ignorealarm`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `fta_solutions_app_ignorealarm` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cc_biz_id` int(11) NOT NULL,
  `alarm_type` varchar(255) DEFAULT NULL,
  `attr_id` varchar(512) DEFAULT NULL,
  `cc_module` varchar(512) DEFAULT NULL,
  `note` longtext NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fta_solutions_app_ignorealarm`
--

LOCK TABLES `fta_solutions_app_ignorealarm` WRITE;
/*!40000 ALTER TABLE `fta_solutions_app_ignorealarm` DISABLE KEYS */;
/*!40000 ALTER TABLE `fta_solutions_app_ignorealarm` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fta_solutions_app_incident`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `fta_solutions_app_incident` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `is_visible` tinyint(1) NOT NULL,
  `incident_def_id` int(11) NOT NULL,
  `incident_type` varchar(128) DEFAULT NULL,
  `cc_biz_id` int(11) NOT NULL,
  `dimension` varchar(128) NOT NULL,
  `description` longtext NOT NULL,
  `content` longtext NOT NULL,
  `detail` longtext,
  `last_check_time` datetime NOT NULL,
  `begin_time` datetime NOT NULL,
  `end_time` datetime DEFAULT NULL,
  `notify_status` varchar(4) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `dimension` (`dimension`),
  KEY `fta_solutions_app_incident_4b555eec` (`incident_def_id`),
  KEY `fta_solutions_app_incident_3151d52d` (`incident_type`),
  KEY `fta_solutions_app_incident_5b14b3ac` (`cc_biz_id`),
  KEY `fta_solutions_app_incident_9bf533b7` (`begin_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fta_solutions_app_incident`
--

LOCK TABLES `fta_solutions_app_incident` WRITE;
/*!40000 ALTER TABLE `fta_solutions_app_incident` DISABLE KEYS */;
/*!40000 ALTER TABLE `fta_solutions_app_incident` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fta_solutions_app_incidentalarm`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `fta_solutions_app_incidentalarm` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `incident_id` int(11) NOT NULL,
  `alarm_id` int(11) NOT NULL,
  `is_primary` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `fta_solutions_app_incidentalar_incident_id_7885b719f404a6c5_uniq` (`incident_id`,`alarm_id`),
  KEY `fta_solutions_app_incidentalarm_f5ce6141` (`incident_id`),
  KEY `fta_solutions_app_incidentalarm_b1f918f6` (`alarm_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fta_solutions_app_incidentalarm`
--

LOCK TABLES `fta_solutions_app_incidentalarm` WRITE;
/*!40000 ALTER TABLE `fta_solutions_app_incidentalarm` DISABLE KEYS */;
/*!40000 ALTER TABLE `fta_solutions_app_incidentalarm` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fta_solutions_app_incidentdef`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `fta_solutions_app_incidentdef` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `is_enabled` tinyint(1) NOT NULL,
  `cc_biz_id` int(11) NOT NULL,
  `codename` varchar(128) NOT NULL,
  `rule` longtext NOT NULL,
  `description` longtext NOT NULL,
  `exclude` longtext,
  `priority` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `fta_solutions_app_incidentdef_cc_biz_id_5b78b22401899362_uniq` (`cc_biz_id`,`codename`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fta_solutions_app_incidentdef`
--

LOCK TABLES `fta_solutions_app_incidentdef` WRITE;
/*!40000 ALTER TABLE `fta_solutions_app_incidentdef` DISABLE KEYS */;
INSERT INTO `fta_solutions_app_incidentdef` VALUES (2,1,0,'same_solution','{\n    \"alarm_type\": [\n        \"ZABBIX-icmping*\",\n        \"NAGIOS-ping\",\n        \"BASE_ALARM_3\"\n    ],\n    \"timedelta\": 5,\n    \"count\": 1,\n    \"incident\": \"skip\",\n    \"condition\": {\n        \"solution\": [\n            \"self\"\n        ],\n        \"host\": [\n            \"self\"\n        ],\n        \"alarm_type\": [\n            \"ZABBIX-icmping*\",\n            \"NAGIOS-ping\",\n            \"BASE_ALARM_3\"\n        ]\n    }\n}','一系列处理套餐相同的告警（同一起事件造成的多个告警）','',50),(5,1,0,'ping_and_agent_time_out','{\n    \"alarm_type\": [\n        \"ZABBIX-icmping*\",\n        \"NAGIOS-ping\",\n        \"BASE_ALARM_3\"\n    ],\n    \"timedelta\": 5,\n    \"count\": 1,\n    \"incident\": \"skip\",\n    \"condition\": {\n        \"alarm_type\": [\n            \"ZABBIX-icmping*\",\n            \"NAGIOS-ping\",\n            \"BASE_ALARM_3\"\n        ],\n        \"host\": [\n            \"self\"\n        ]\n    }\n}','一系列单机异常类告警（同一起事件造成的多个告警）','',30);
/*!40000 ALTER TABLE `fta_solutions_app_incidentdef` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fta_solutions_app_incorder`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `fta_solutions_app_incorder` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `inc_orderno` varchar(255) NOT NULL,
  `alarm_id` int(11) NOT NULL,
  `push_type` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `inc_orderno` (`inc_orderno`),
  UNIQUE KEY `fta_solutions_app_incorder_alarm_id_7d4e2a14424538b0_uniq` (`alarm_id`,`push_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fta_solutions_app_incorder`
--

LOCK TABLES `fta_solutions_app_incorder` WRITE;
/*!40000 ALTER TABLE `fta_solutions_app_incorder` DISABLE KEYS */;
/*!40000 ALTER TABLE `fta_solutions_app_incorder` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fta_solutions_app_increlatedalarm`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `fta_solutions_app_increlatedalarm` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `orderno` varchar(255) NOT NULL,
  `trigger_orderno` varchar(255) NOT NULL,
  `product_id` varchar(255) NOT NULL,
  `server_ip` varchar(255) DEFAULT NULL,
  `category_id` int(11) NOT NULL,
  `archive` varchar(255) NOT NULL,
  `level` int(11) NOT NULL,
  `trigger_start_time` datetime NOT NULL,
  `trigger_end_time` datetime DEFAULT NULL,
  `content` varchar(512) DEFAULT NULL,
  `affect` varchar(512) DEFAULT NULL,
  `strategy` varchar(512) DEFAULT NULL,
  `remark` varchar(512) DEFAULT NULL,
  `url` varchar(512) DEFAULT NULL,
  `responsible_people` varchar(512) NOT NULL,
  `trigger_fault` int(11) NOT NULL,
  `trigger_description` varchar(512) DEFAULT NULL,
  `ticket_type` int(11) DEFAULT NULL,
  `ticket_name` varchar(255) DEFAULT NULL,
  `ticket_no` varchar(512) DEFAULT NULL,
  `ticket_url` varchar(512) DEFAULT NULL,
  `ticket_description` varchar(512) DEFAULT NULL,
  `ticket_reason` varchar(512) DEFAULT NULL,
  `ticket_summary` varchar(512) DEFAULT NULL,
  `status` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `orderno` (`orderno`),
  KEY `fta_solutions_app_increlatedalarm_888d0ee3` (`archive`),
  KEY `fta_solutions_app_increlatedalarm_e2ddf85b` (`trigger_start_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fta_solutions_app_increlatedalarm`
--

LOCK TABLES `fta_solutions_app_increlatedalarm` WRITE;
/*!40000 ALTER TABLE `fta_solutions_app_increlatedalarm` DISABLE KEYS */;
/*!40000 ALTER TABLE `fta_solutions_app_increlatedalarm` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fta_solutions_app_kpicache`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `fta_solutions_app_kpicache` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date` date NOT NULL,
  `cc_biz_id` int(11) NOT NULL,
  `kpi_type` int(10) unsigned NOT NULL,
  `tnm_total` int(10) unsigned NOT NULL,
  `tnm_covered` int(10) unsigned NOT NULL,
  `tnm_success` int(10) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `fta_solutions_app_kpicache_date_24e23487f48f6a0e_uniq` (`date`,`cc_biz_id`,`kpi_type`),
  KEY `fta_solutions_app_kpicache_5fc73231` (`date`),
  KEY `fta_solutions_app_kpicache_5b14b3ac` (`cc_biz_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fta_solutions_app_kpicache`
--

LOCK TABLES `fta_solutions_app_kpicache` WRITE;
/*!40000 ALTER TABLE `fta_solutions_app_kpicache` DISABLE KEYS */;
/*!40000 ALTER TABLE `fta_solutions_app_kpicache` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fta_solutions_app_outofscopearchive`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `fta_solutions_app_outofscopearchive` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cc_biz_id` int(11) NOT NULL,
  `alarm_type` varchar(255) NOT NULL,
  `cc_module` varchar(128) DEFAULT NULL,
  `sub_count` int(10) unsigned NOT NULL,
  `cc_set_name` varchar(128),
  `created_on` datetime NOT NULL,
  `extra` longtext,
  `updated_on` datetime NOT NULL,
  `status` varchar(10) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `fta_solutions_app_outofscopearch_cc_biz_id_78ab4251737f9464_uniq` (`cc_biz_id`,`alarm_type`,`cc_module`,`cc_set_name`),
  KEY `fta_solutions_app_outofscopearchive_5b14b3ac` (`cc_biz_id`),
  KEY `fta_solutions_app_outofscopearchive_1e677533` (`alarm_type`),
  KEY `fta_solutions_app_outofscopearchive_cfa10352` (`cc_module`),
  KEY `fta_solutions_app_outofscopearchive_83991a2b` (`cc_set_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fta_solutions_app_outofscopearchive`
--

LOCK TABLES `fta_solutions_app_outofscopearchive` WRITE;
/*!40000 ALTER TABLE `fta_solutions_app_outofscopearchive` DISABLE KEYS */;
/*!40000 ALTER TABLE `fta_solutions_app_outofscopearchive` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fta_solutions_app_qcloudownerinfo`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `fta_solutions_app_qcloudownerinfo` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `owner_uin` varchar(50) NOT NULL,
  `qcloud_app_id` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `owner_uin` (`owner_uin`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fta_solutions_app_qcloudownerinfo`
--

LOCK TABLES `fta_solutions_app_qcloudownerinfo` WRITE;
/*!40000 ALTER TABLE `fta_solutions_app_qcloudownerinfo` DISABLE KEYS */;
/*!40000 ALTER TABLE `fta_solutions_app_qcloudownerinfo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fta_solutions_app_solution`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `fta_solutions_app_solution` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cc_biz_id` int(11) NOT NULL,
  `solution_type` varchar(128) NOT NULL,
  `codename` varchar(128) DEFAULT NULL,
  `title` varchar(512) NOT NULL,
  `config` longtext,
  `creator` varchar(255) NOT NULL,
  `create_time` datetime NOT NULL,
  `create_user` varchar(32) NOT NULL,
  `update_time` datetime NOT NULL,
  `update_user` varchar(32) NOT NULL,
  `is_deleted` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fta_solutions_app_solution_5b14b3ac` (`cc_biz_id`)
) ENGINE=InnoDB AUTO_INCREMENT=41 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fta_solutions_app_solution`
--

LOCK TABLES `fta_solutions_app_solution` WRITE;
/*!40000 ALTER TABLE `fta_solutions_app_solution` DISABLE KEYS */;
INSERT INTO `fta_solutions_app_solution` VALUES (4,0,'switch_ip','diy_only','『快捷』后续处理对象故障机与备机互换',' {}','管理员','2017-09-05 19:14:33','','2017-09-05 19:14:33','',0),(5,0,'bk_component','diy_only','『快捷』CC拷贝故障机属性到备机','{\"module_name\":\"bk.cc\",\"task_name\":\"clone_host_property\",\"task_kwargs\":\"{\\n    \\\"uin\\\": \\\"100\\\",\\n    \\\"operator\\\": \\\"${operator}\\\",\\n \\\"app_id\\\": \\\"${cc_biz_id}\\\",\\n    \\\"plat_id\\\":\\\"${cc|plat_id}\\\",\\n    \\\"org_ip\\\":\\\"${bpm_context|alarm_ci_name}\\\" ,\\n    \\\"dst_ip\\\":\\\"${bpm_context|ip_bak}\\\"   \\n}\"}','管理员','2017-09-05 19:14:33','','2017-09-05 19:14:33','',0),(6,0,'bk_component','diy_only','『快捷』CC移到“空闲机”模块','{\"module_name\":\"bk.cc\",\"task_name\":\"update_host_module\",\"task_kwargs\":\"{\\n    \\\"uin\\\": \\\"100\\\",\\n    \\\"operator\\\": \\\"${operator}\\\",\\n\\\"app_id\\\": \\\"${cc_biz_id}\\\", \\n    \\\"plat_id\\\": \\\"${cc|plat_id}\\\",\\n    \\\"dst_module_id\\\": \\\"${cc|idle_module_id}\\\",\\n    \\\"ip\\\": \\\"${ip}\\\"\\n}\"}','管理员','2017-09-05 19:14:33','','2017-09-05 19:14:33','',0),(7,0,'ijobs','non-display','『Non-Display』获取内存使用率TOP10的进程','{\"app_id\":\"77770001\",\"task_id\":\"3\",\"ijobs_taski_name\":\"『快捷』获取内存使用率TOP10的进程\",\"parms\":\"\",\"parms0\":\"\",\"argv\":\"on\",\"retry_time\":\"10\",\"retry_count\":\"2\",\"steps\":\"1\",\"operator\":\"100\"}','管理员','2017-09-05 19:14:33','','2017-09-05 19:14:33','',0),(8,0,'ijobs','non-display','『Non-Display』获取CPU使用率TOP10的进程','{\"app_id\":\"77770001\",\"task_id\":\"2\",\"ijobs_taski_name\":\"『快捷』获取CPU使用率TOP10的进程\",\"parms\":\"\",\"parms0\":\"\",\"argv\":\"on\",\"retry_time\":\"10\",\"retry_count\":\"2\",\"steps\":\"1\",\"operator\":\"100\"}','管理员','2017-09-05 19:14:33','','2017-09-05 19:14:33','',0),(9,0,'notice','non-display','『Non-Display』发送CPU使用率TOP10的进程(微信)','{\"message\":\"【故障自愈】CPU使用率TOP10列表：\\n业务：\\\"${cc|ApplicationName}\\\"\\n模块：\\\"${cc|ModuleName}\\\"\\n主机：${ip}\\n---------------------------------------\\n${bpm_context|ijobs_return_cpu}\",\"extra_people\":\"\",\"extra_people_select\":null,\"wechat\":\"on\"}','管理员','2017-09-05 19:14:33','','2017-09-05 19:14:33','',0),(10,0,'graph','cpu_proc_top10','『快捷』发送CPU使用率TOP10的进程(微信)','{\"real_solutions\":\"[[{\\\"1\\\": [\\\"success\\\"]}, \\\"8\\\"], [{}, \\\"9\\\"]]\"}','管理员','2017-09-05 19:14:33','','2017-09-05 19:14:33','',0),(24,0,'notice','non-display','『Non-Display』发送内存使用率TOP10的进程(微信)','{\"message\":\"【故障自愈】内存使用率TOP10列表：\\n业务：\\\"${cc|ApplicationName}\\\"\\n模块：\\\"${cc|ModuleName}\\\"\\n主机：${ip}\\n---------------------------------------\\n${bpm_context|ijobs_return_mem}\",\"extra_people\":\"\",\"extra_people_select\":null,\"wechat\":\"on\"}','管理员','2017-09-05 19:14:33','','2017-09-05 19:14:33','',0),(25,0,'graph','mem_proc_top10','『快捷』发送内存使用率TOP10的进程(微信)','{\"real_solutions\":\"[[{\\\"1\\\": [\\\"success\\\"]}, \\\"7\\\"], [{}, \\\"24\\\"]]\"}','管理员','2017-09-05 19:14:33','','2017-09-05 19:14:33','',0),(36,0,'bk_component','cc_to_fault_module','『快捷』CC移到“故障机”模块','{\"module_name\":\"bk.cc\",\"task_name\":\"update_host_module\",\"task_kwargs\":\"{\\n    \\\"uin\\\": \\\"100\\\",\\n    \\\"operator\\\": \\\"${operator}\\\",\\n\\\"app_id\\\": \\\"${cc_biz_id}\\\", \\n    \\\"plat_id\\\": \\\"${cc|plat_id}\\\",\\n    \\\"dst_module_id\\\": \\\"${cc|fault_module_id}\\\",\\n    \\\"ip\\\": \\\"${ip}\\\" \\n}\"}','管理员','2017-09-05 19:14:33','','2017-09-05 19:14:33','',0),(37,0,'notice','non-display','『Non-Display』发送CPU使用率TOP10的进程(短信)','{\"message\":\"【故障自愈】CPU使用率TOP10列表：\\n业务：\\\"${cc|ApplicationName}\\\"\\n模块：\\\"${cc|ModuleName}\\\"\\n主机：${ip}\\n---------------------------------------\\n${bpm_context|ijobs_return_cpu}\",\"extra_people\":\"\",\"extra_people_select\":null,\"sms\":\"on\"}','管理员','2017-09-05 19:14:33','','2017-09-05 19:14:33','',0),(38,0,'notice','non-display','『Non-Display』发送CPU使用率TOP10的进程(邮件)','{\"message\":\"【故障自愈】CPU使用率TOP10列表：\\n业务：\\\"${cc|ApplicationName}\\\"\\n模块：\\\"${cc|ModuleName}\\\"\\n主机：${ip}\\n---------------------------------------\\n${bpm_context|ijobs_return_cpu}\",\"extra_people\":\"\",\"extra_people_select\":null,\"email\":\"on\"}','管理员','2017-09-05 19:14:33','','2017-09-05 19:14:33','',0),(39,0,'notice','non-display','『Non-Display』发送内存使用率TOP10的进程(短信)','{\"message\":\"【故障自愈】内存使用率TOP10列表：\\n业务：\\\"${cc|ApplicationName}\\\"\\n模块：\\\"${cc|ModuleName}\\\"\\n主机：${ip}\\n---------------------------------------\\n${bpm_context|ijobs_return_mem}\",\"extra_people\":\"\",\"extra_people_select\":null,\"sms\":\"on\"}','管理员','2017-09-05 19:14:33','','2017-09-05 19:14:33','',0),(40,0,'notice','non-display','『Non-Display』发送内存使用率TOP10的进程(邮件)','{\"message\":\"【故障自愈】内存使用率TOP10列表：\\n业务：\\\"${cc|ApplicationName}\\\"\\n模块：\\\"${cc|ModuleName}\\\"\\n主机：${ip}\\n---------------------------------------\\n${bpm_context|ijobs_return_mem}\",\"extra_people\":\"\",\"extra_people_select\":null,\"email\":\"on\"}','管理员','2017-09-05 19:14:33','','2017-09-05 19:14:33','',0);
/*!40000 ALTER TABLE `fta_solutions_app_solution` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fta_solutions_app_useraction`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `fta_solutions_app_useraction` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(255) NOT NULL,
  `is_guide` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fta_solutions_app_useraction`
--

LOCK TABLES `fta_solutions_app_useraction` WRITE;
/*!40000 ALTER TABLE `fta_solutions_app_useraction` DISABLE KEYS */;
/*!40000 ALTER TABLE `fta_solutions_app_useraction` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fta_solutions_app_userbiz`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `fta_solutions_app_userbiz` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(255) NOT NULL,
  `cc_biz_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fta_solutions_app_userbiz`
--

LOCK TABLES `fta_solutions_app_userbiz` WRITE;
/*!40000 ALTER TABLE `fta_solutions_app_userbiz` DISABLE KEYS */;
/*!40000 ALTER TABLE `fta_solutions_app_userbiz` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fta_solutions_app_world`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `fta_solutions_app_world` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `is_enabled` tinyint(1) NOT NULL,
  `cc_biz_id` int(11) NOT NULL,
  `cc_set_name` varchar(30) NOT NULL,
  `cc_set_chn_name` varchar(30) NOT NULL,
  `world_id` varchar(30) NOT NULL,
  `tnm_attr_id` varchar(30) DEFAULT NULL,
  `tnm_attr_name` varchar(255) DEFAULT NULL,
  `comment` longtext,
  `online_data_source_host` char(15) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fta_solutions_app_world_5b14b3ac` (`cc_biz_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fta_solutions_app_world`
--

LOCK TABLES `fta_solutions_app_world` WRITE;
/*!40000 ALTER TABLE `fta_solutions_app_world` DISABLE KEYS */;
/*!40000 ALTER TABLE `fta_solutions_app_world` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `guardian_groupobjectpermission`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `guardian_groupobjectpermission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `object_pk` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `guardian_groupobjectpermission_group_id_1692da556eb7175b_uniq` (`group_id`,`permission_id`,`object_pk`),
  KEY `guard_content_type_id_597c953df5d1232d_fk_django_content_type_id` (`content_type_id`),
  KEY `guardian_gr_permission_id_6db56426ae60788a_fk_auth_permission_id` (`permission_id`),
  CONSTRAINT `guard_content_type_id_597c953df5d1232d_fk_django_content_type_id` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `guardian_gr_permission_id_6db56426ae60788a_fk_auth_permission_id` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `guardian_groupobjectp_group_id_713e154dfd2f5937_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `guardian_groupobjectpermission`
--

LOCK TABLES `guardian_groupobjectpermission` WRITE;
/*!40000 ALTER TABLE `guardian_groupobjectpermission` DISABLE KEYS */;
/*!40000 ALTER TABLE `guardian_groupobjectpermission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `guardian_userobjectpermission`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `guardian_userobjectpermission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `object_pk` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `guardian_userobjectpermission_user_id_3d019018f740de5f_uniq` (`user_id`,`permission_id`,`object_pk`),
  KEY `guard_content_type_id_1d41cfa581d8d978_fk_django_content_type_id` (`content_type_id`),
  KEY `guardian_us_permission_id_2e655ff0bbafb1c1_fk_auth_permission_id` (`permission_id`),
  CONSTRAINT `guard_content_type_id_1d41cfa581d8d978_fk_django_content_type_id` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `guardian_us_permission_id_2e655ff0bbafb1c1_fk_auth_permission_id` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `guardian_userobjec_user_id_4727c7e419caead5_fk_account_bkuser_id` FOREIGN KEY (`user_id`) REFERENCES `account_bkuser` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `guardian_userobjectpermission`
--

LOCK TABLES `guardian_userobjectpermission` WRITE;
/*!40000 ALTER TABLE `guardian_userobjectpermission` DISABLE KEYS */;
/*!40000 ALTER TABLE `guardian_userobjectpermission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `permission_business`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `permission_business` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cc_id` int(11) NOT NULL,
  `cc_name` varchar(100) NOT NULL,
  `cc_owner` varchar(100) NOT NULL,
  `cc_company` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `cc_id` (`cc_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `permission_business`
--

LOCK TABLES `permission_business` WRITE;
/*!40000 ALTER TABLE `permission_business` DISABLE KEYS */;
/*!40000 ALTER TABLE `permission_business` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `permission_businessgroupmembership`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `permission_businessgroupmembership` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date_created` datetime NOT NULL,
  `business_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `permission_businessgroupmember_business_id_2537942a5833faa9_uniq` (`business_id`,`group_id`),
  KEY `permission_businessgr_group_id_48594ebd715fe34b_fk_auth_group_id` (`group_id`),
  CONSTRAINT `permissio_business_id_4430c6e45b7d3d37_fk_permission_business_id` FOREIGN KEY (`business_id`) REFERENCES `permission_business` (`id`),
  CONSTRAINT `permission_businessgr_group_id_48594ebd715fe34b_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `permission_businessgroupmembership`
--

LOCK TABLES `permission_businessgroupmembership` WRITE;
/*!40000 ALTER TABLE `permission_businessgroupmembership` DISABLE KEYS */;
/*!40000 ALTER TABLE `permission_businessgroupmembership` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `permission_loignlog`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `permission_loignlog` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `login_time` datetime NOT NULL,
  `login_browser` varchar(200) DEFAULT NULL,
  `login_ip` varchar(50) DEFAULT NULL,
  `login_host` varchar(100) DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `permission_loignlo_user_id_554b9411a5805c03_fk_account_bkuser_id` (`user_id`),
  CONSTRAINT `permission_loignlo_user_id_554b9411a5805c03_fk_account_bkuser_id` FOREIGN KEY (`user_id`) REFERENCES `account_bkuser` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `permission_loignlog`
--

LOCK TABLES `permission_loignlog` WRITE;
/*!40000 ALTER TABLE `permission_loignlog` DISABLE KEYS */;
/*!40000 ALTER TABLE `permission_loignlog` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `permission_userbusiness`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `permission_userbusiness` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user` varchar(255) NOT NULL,
  `default_buss` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user` (`user`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `permission_userbusiness`
--

LOCK TABLES `permission_userbusiness` WRITE;
/*!40000 ALTER TABLE `permission_userbusiness` DISABLE KEYS */;
/*!40000 ALTER TABLE `permission_userbusiness` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tastypie_apiaccess`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tastypie_apiaccess` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `identifier` varchar(255) NOT NULL,
  `url` varchar(255) NOT NULL,
  `request_method` varchar(10) NOT NULL,
  `accessed` int(10) unsigned NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tastypie_apiaccess`
--

LOCK TABLES `tastypie_apiaccess` WRITE;
/*!40000 ALTER TABLE `tastypie_apiaccess` DISABLE KEYS */;
/*!40000 ALTER TABLE `tastypie_apiaccess` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tastypie_apikey`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tastypie_apikey` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `key` varchar(128) NOT NULL,
  `created` datetime NOT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  KEY `tastypie_apikey_3c6e0b8a` (`key`),
  CONSTRAINT `tastypie_apikey_user_id_ffeb4840e0b406b_fk_account_bkuser_id` FOREIGN KEY (`user_id`) REFERENCES `account_bkuser` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tastypie_apikey`
--

LOCK TABLES `tastypie_apikey` WRITE;
/*!40000 ALTER TABLE `tastypie_apikey` DISABLE KEYS */;
/*!40000 ALTER TABLE `tastypie_apikey` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_activity_log`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_activity_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `log_id` varchar(32) NOT NULL,
  `app_code` varchar(32) NOT NULL,
  `username` varchar(32) NOT NULL,
  `activity_type` int(11) NOT NULL,
  `activity_name` varchar(100) NOT NULL,
  `request_params` longtext,
  `before_data` longtext,
  `after_data` longtext,
  `activity_time` datetime NOT NULL,
  `remarks` longtext,
  PRIMARY KEY (`id`),
  KEY `user_activity_log_5072fa9e` (`log_id`)
) ENGINE=InnoDB AUTO_INCREMENT=70 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_activity_log`
--

LOCK TABLES `user_activity_log` WRITE;
/*!40000 ALTER TABLE `user_activity_log` DISABLE KEYS */;
INSERT INTO `user_activity_log` VALUES (1,'d9f23b26830247528f8ae76ef9a845e0','0','*NONAME*',2,'新增告警类型[1]: 5分钟平均负载（乘以100)','告警类型','','','2017-09-05 19:14:32',''),(2,'dce364d00f7942699f5be6415942f08e','0','*NONAME*',2,'新增告警类型[2]: cpu总使用率','告警类型','','','2017-09-05 19:14:32',''),(3,'b2f25b688de74240ba530da2cf1885c3','0','*NONAME*',2,'新增告警类型[3]: cpu单核使用率','告警类型','','','2017-09-05 19:14:32',''),(4,'bd1af6d269704525819963babed35874','0','*NONAME*',2,'新增告警类型[4]: 应用程序使用内存量','告警类型','','','2017-09-05 19:14:32',''),(5,'06d740304f3d480889dea4eb87b67570','0','*NONAME*',2,'新增告警类型[5]: 物理内存使用率','告警类型','','','2017-09-05 19:14:32',''),(6,'3ae2ce019023497eadd0006b22bd277c','0','*NONAME*',2,'新增告警类型[6]: 已用物理内存','告警类型','','','2017-09-05 19:14:32',''),(7,'955daca6a75c45e6a679e9f277ed9d69','0','*NONAME*',2,'新增告警类型[7]: 网卡入流量','告警类型','','','2017-09-05 19:14:32',''),(8,'67e02ee76fde4b7b99e0253cb0848f6d','0','*NONAME*',2,'新增告警类型[8]: 网卡出流量','告警类型','','','2017-09-05 19:14:32',''),(9,'556e268a874b4a56b76ae6154d9ce699','0','*NONAME*',2,'新增告警类型[9]: 网卡发包量','告警类型','','','2017-09-05 19:14:32',''),(10,'7f5e5a7410d04b5bb53052cf3bceb049','0','*NONAME*',2,'新增告警类型[10]: 网卡收包量','告警类型','','','2017-09-05 19:14:32',''),(11,'5c854e964b234ac1a7cf7a19afdaa4ec','0','*NONAME*',2,'新增告警类型[11]: 已用空间占比','告警类型','','','2017-09-05 19:14:32',''),(12,'e58d3a71bf924532a7e5427a88e9e38b','0','*NONAME*',2,'新增告警类型[12]: 磁盘IO读速率','告警类型','','','2017-09-05 19:14:32',''),(13,'8f4bb2f4a6b34b34bbafcd372689673c','0','*NONAME*',2,'新增告警类型[13]: 磁盘IO写速率','告警类型','','','2017-09-05 19:14:32',''),(14,'76683c9b223b45dba542ba339f0e7400','0','*NONAME*',2,'新增告警类型[14]: 磁盘IO使用率','告警类型','','','2017-09-05 19:14:32',''),(15,'aae729b997a64c0988ba1f13a946ed53','0','*NONAME*',2,'新增告警类型[15]: 磁盘只读','告警类型','','','2017-09-05 19:14:32',''),(16,'b17c22e968294af0972df74761c317fb','0','*NONAME*',2,'新增告警类型[16]: 磁盘写满','告警类型','','','2017-09-05 19:14:32',''),(17,'d9598f12f2ad4b9f9aa56db1d9b59b5d','0','*NONAME*',2,'新增告警类型[17]: Corefile产生','告警类型','','','2017-09-05 19:14:32',''),(18,'7606d8eb3f82462e8dea75b939e5484f','0','*NONAME*',2,'新增告警类型[18]: 自定义','告警类型','','','2017-09-05 19:14:32',''),(19,'a5a9125ea84f434a8d8e6a7c5c1b60cd','0','*NONAME*',2,'新增告警类型[19]: Agent状态(agent.*)','告警类型','','','2017-09-05 19:14:32',''),(20,'a0967c0181d0416eaaa5c8779bbe863e','0','*NONAME*',2,'新增告警类型[20]: CPU使用率(system.cpu.*)','告警类型','','','2017-09-05 19:14:32',''),(21,'5bef215d292349929c7e1b37d1a3ed52','0','*NONAME*',2,'新增告警类型[21]: 内存使用量(vm.memory.size)','告警类型','','','2017-09-05 19:14:32',''),(22,'0e6c3f38624943b9801acebc040274a8','0','*NONAME*',2,'新增告警类型[22]: Swap使用量(system.swap.*)','告警类型','','','2017-09-05 19:14:32',''),(23,'94e7466c108a4420bb3084c7c8bc8a5e','0','*NONAME*',2,'新增告警类型[23]: 系统内核状态(kernel.*)','告警类型','','','2017-09-05 19:14:32',''),(24,'37ae35418554403ba5f732c53684d76d','0','*NONAME*',2,'新增告警类型[24]: 磁盘IO使用率(vfs.dev.*)','告警类型','','','2017-09-05 19:14:32',''),(25,'5e5fe13383d549cbaa1530e47dc2fd36','0','*NONAME*',2,'新增告警类型[25]: 磁盘容量(vfs.fs.*)','告警类型','','','2017-09-05 19:14:32',''),(26,'1d540503fdc24acbb37c269fbe968a1d','0','*NONAME*',2,'新增告警类型[26]: 进程数量检查(proc.num)','告警类型','','','2017-09-05 19:14:32',''),(27,'19e3a2be837045eeb2cd1fb8dc1a4263','0','*NONAME*',2,'新增告警类型[27]: Ping检查(icmpping*)','告警类型','','','2017-09-05 19:14:32',''),(28,'e634f84d25c3437c8e00dd7c573745df','0','*NONAME*',2,'新增告警类型[28]: TCP链接检查(net.tcp.*)','告警类型','','','2017-09-05 19:14:32',''),(29,'d71c9d3fee654b2794dceae5a27c178e','0','*NONAME*',2,'新增告警类型[29]: UDP链接检查(net.udp.*)','告警类型','','','2017-09-05 19:14:32',''),(30,'4388f51465d64c73ba9bbcee9c9f0fd4','0','*NONAME*',2,'新增告警类型[30]: 文件状态检查(vfs.file.*)','告警类型','','','2017-09-05 19:14:32',''),(31,'0470a5a2cf90450eaac4d00d89882924','0','*NONAME*',2,'新增告警类型[31]: Zabbix其他','告警类型','','','2017-09-05 19:14:32',''),(32,'25f15e73bc22449f9b4333740615ea5d','0','*NONAME*',2,'新增告警类型[32]: HTTP(http)','告警类型','','','2017-09-05 19:14:32',''),(33,'17363a84ce804b76b5ab1c43ec3a0edc','0','*NONAME*',2,'新增告警类型[33]: CPU(cpu)','告警类型','','','2017-09-05 19:14:32',''),(34,'913d628bb00a465eb0adb94c068487a1','0','*NONAME*',2,'新增告警类型[34]: 内存(memory)','告警类型','','','2017-09-05 19:14:32',''),(35,'6ef8b8c56f374f0bb542e8e390d2f822','0','*NONAME*',2,'新增告警类型[35]: 网络(net)','告警类型','','','2017-09-05 19:14:32',''),(36,'8955fb7d3d6d4e2b9d7cc01f96bb50f1','0','*NONAME*',2,'新增告警类型[36]: 文件系统(filesystem)','告警类型','','','2017-09-05 19:14:32',''),(37,'7abf26e15a674e65b921941b46cbc239','0','*NONAME*',2,'新增告警类型[37]: 磁盘(disk)','告警类型','','','2017-09-05 19:14:32',''),(38,'d13f20dfeae44c9db05f3ff9f057e28b','0','*NONAME*',2,'新增告警类型[38]: 进程(process)','告警类型','','','2017-09-05 19:14:32',''),(39,'1bec24d892b5499e9a5e34b5f331cc94','0','*NONAME*',2,'新增告警类型[39]: Ping','告警类型','','','2017-09-05 19:14:32',''),(40,'15087170f1c84e938c3b3a3dedbf3f42','0','*NONAME*',2,'新增告警类型[40]: Nagios其他(nagios)','告警类型','','','2017-09-05 19:14:32',''),(41,'aaac4b6b5524457b9e93a545d5ea2c44','0','*NONAME*',2,'新增告警类型[41]: Agent状态(agent.*)','告警类型','','','2017-09-05 19:14:32',''),(42,'60fb523a0fb64a29882ea120b71d96fb','0','*NONAME*',2,'新增告警类型[42]: CPU使用率(load.*)','告警类型','','','2017-09-05 19:14:32',''),(43,'c15fc32fc8df47bf933d2aa448ee6f14','0','*NONAME*',2,'新增告警类型[43]: 内存使用量(mem.*)','告警类型','','','2017-09-05 19:14:32',''),(44,'219a1548d6384806a6e3b8896ce908a1','0','*NONAME*',2,'新增告警类型[44]: 磁盘IO使用率(disk.io.*)','告警类型','','','2017-09-05 19:14:32',''),(45,'89cb314f10de47edb5136079f5e6ed13','0','*NONAME*',2,'新增告警类型[45]: 磁盘容量(df.*)','告警类型','','','2017-09-05 19:14:32',''),(46,'5c5c73dcbd03418d8a2e88ce9b3633d4','0','*NONAME*',2,'新增告警类型[46]: 网卡流量(net.if.*)','告警类型','','','2017-09-05 19:14:32',''),(47,'9f2c7994751f45f6a04ddd07c91d46c2','0','*NONAME*',2,'新增告警类型[47]: 端口监控(net.port.listen)','告警类型','','','2017-09-05 19:14:32',''),(48,'b3e564dd258e4f638ab4362bd9a7b14e','0','*NONAME*',2,'新增告警类型[48]: Open-falcon其他','告警类型','','','2017-09-05 19:14:32',''),(49,'d2c741888ece46c2872e1cff0c30bc77','0','*NONAME*',2,'新增告警类型[49]: REST默认分类','告警类型','','','2017-09-05 19:14:32',''),(50,'56510a43b8ff4874a08712e92f648b31','0','*NONAME*',2,'新增告警类型[50]: 预警自愈','告警类型','','','2017-09-05 19:14:32',''),(51,'69d483039dee4327a9b7ef4528283e60','0','*NONAME*',2,'新增告警类型[51]: 默认分类','告警类型','','','2017-09-05 19:14:32',''),(52,'aa0a02947b0240598a9bf9d7fd8fe665','0','*NONAME*',2,'新增收敛规则[5]: 一系列单机异常类告警（同一起事件造成的多个告警）','收敛规则','','','2017-09-05 19:14:33',''),(53,'7a4a66e7591640748e74970b8d7a9b81','0','*NONAME*',2,'新增收敛规则[2]: 一系列处理套餐相同的告警（同一起事件造成的多个告警）','收敛规则','','','2017-09-05 19:14:33',''),(54,'37a6afaff6454c5188669ca4f515560e','0','*NONAME*',2,'新增自愈套餐[4]: 『快捷』后续处理对象故障机与备机互换','自愈套餐','','','2017-09-05 19:14:33',''),(55,'b815949162824526aa8dbac312b9739f','0','*NONAME*',2,'新增自愈套餐[5]: 『快捷』CC拷贝故障机属性到备机','自愈套餐','','','2017-09-05 19:14:33',''),(56,'ec18d5a1b67c41ddb77d882a8c79e6fd','0','*NONAME*',2,'新增自愈套餐[6]: 『快捷』CC移到“空闲机”模块','自愈套餐','','','2017-09-05 19:14:33',''),(57,'2b5df1e223084f8b88a768a08e478b62','0','*NONAME*',2,'新增自愈套餐[7]: 『Non-Display』获取内存使用率TOP10的进程','自愈套餐','','','2017-09-05 19:14:33',''),(58,'9719dce1c9c94377b81ab68fcb991503','0','*NONAME*',2,'新增自愈套餐[8]: 『Non-Display』获取CPU使用率TOP10的进程','自愈套餐','','','2017-09-05 19:14:33',''),(59,'257290775b5c450eb01e461a067822db','0','*NONAME*',2,'新增自愈套餐[9]: 『Non-Display』发送CPU使用率TOP10的进程(微信)','自愈套餐','','','2017-09-05 19:14:33',''),(60,'7bcecb1facf04e79870b4f85faba8b2e','0','*NONAME*',2,'新增自愈套餐[10]: 『快捷』发送CPU使用率TOP10的进程(微信)','自愈套餐','','','2017-09-05 19:14:33',''),(61,'f7ba6ba9d2354a0782733e2f64fe3b50','0','*NONAME*',2,'新增自愈套餐[24]: 『Non-Display』发送内存使用率TOP10的进程(微信)','自愈套餐','','','2017-09-05 19:14:33',''),(62,'b8ff30e423d047e9b22ca1a2f168d370','0','*NONAME*',2,'新增自愈套餐[25]: 『快捷』发送内存使用率TOP10的进程(微信)','自愈套餐','','','2017-09-05 19:14:33',''),(63,'77f8ac454d1b4af4a715a0a3bee2b481','0','*NONAME*',2,'新增自愈套餐[36]: 『快捷』CC移到“故障机”模块','自愈套餐','','','2017-09-05 19:14:33',''),(64,'9571253371f24f288a61855d3930a646','0','*NONAME*',2,'新增自愈套餐[37]: 『Non-Display』发送CPU使用率TOP10的进程(短信)','自愈套餐','','','2017-09-05 19:14:33',''),(65,'5a5b660e19f94341bacf3f52d59b06c2','0','*NONAME*',2,'新增自愈套餐[38]: 『Non-Display』发送CPU使用率TOP10的进程(邮件)','自愈套餐','','','2017-09-05 19:14:33',''),(66,'bc0099911cc24e05969e79328faceb14','0','*NONAME*',2,'新增自愈套餐[39]: 『Non-Display』发送内存使用率TOP10的进程(短信)','自愈套餐','','','2017-09-05 19:14:33',''),(67,'58a2daac6d7944ab9732b36c3c6ef16b','0','*NONAME*',2,'新增自愈套餐[40]: 『Non-Display』发送内存使用率TOP10的进程(邮件)','自愈套餐','','','2017-09-05 19:14:33',''),(68,'bd92928c909e4080a263bc6710c12bfb','0','*NONAME*',2,'新增预警自愈[1]: 内置策略','预警自愈','','','2017-09-05 19:14:35',''),(69,'d58a2c3f03d549be8eacf75f2d1d292c','0','*NONAME*',2,'新增告警源[1]: 蓝鲸监控的告警源','告警源','','','2017-09-05 19:14:36','');
/*!40000 ALTER TABLE `user_activity_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wechat_approve`
--

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `wechat_approve` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `obj_id` varchar(255) DEFAULT NULL,
  `message` longtext NOT NULL,
  `callback_url` longtext,
  `status` varchar(32) NOT NULL,
  `approve_users` longtext NOT NULL,
  `approve_by` varchar(128) DEFAULT NULL,
  `approve_at` datetime DEFAULT NULL,
  `create_at` datetime NOT NULL,
  `update_at` datetime NOT NULL,
  `extra` longtext,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wechat_approve`
--

LOCK TABLES `wechat_approve` WRITE;
/*!40000 ALTER TABLE `wechat_approve` DISABLE KEYS */;
/*!40000 ALTER TABLE `wechat_approve` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2017-09-05 19:15:00
