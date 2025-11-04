-- MySQL dump 10.13  Distrib 8.0.40, for Win64 (x86_64)
--
-- Host: localhost    Database: day0425
-- ------------------------------------------------------
-- Server version	8.0.40

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `accessment_studentanswer`
--

DROP TABLE IF EXISTS `accessment_studentanswer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `accessment_studentanswer` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `text` longtext,
  `index` int DEFAULT NULL,
  `type` varchar(50) DEFAULT NULL,
  `score` decimal(5,1) DEFAULT NULL,
  `student_page_record_id` bigint NOT NULL,
  `sub_question_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `accessment_studentan_student_page_record__9ae8b0aa_fk_accessmen` (`student_page_record_id`),
  KEY `accessment_studentan_sub_question_id_8fbba931_fk_ELW_subqu` (`sub_question_id`),
  CONSTRAINT `accessment_studentan_student_page_record__9ae8b0aa_fk_accessmen` FOREIGN KEY (`student_page_record_id`) REFERENCES `accessment_studentpagerecord` (`id`),
  CONSTRAINT `accessment_studentan_sub_question_id_8fbba931_fk_ELW_subqu` FOREIGN KEY (`sub_question_id`) REFERENCES `elw_subquestion` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `accessment_studentanswer`
--

LOCK TABLES `accessment_studentanswer` WRITE;
/*!40000 ALTER TABLE `accessment_studentanswer` DISABLE KEYS */;
/*!40000 ALTER TABLE `accessment_studentanswer` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `accessment_studentexamrecord`
--

DROP TABLE IF EXISTS `accessment_studentexamrecord`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `accessment_studentexamrecord` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `started_at` datetime(6) NOT NULL,
  `ended_at` datetime(6) DEFAULT NULL,
  `finished_at` datetime(6) DEFAULT NULL,
  `submitted` tinyint(1) NOT NULL,
  `integrity_score` decimal(2,1) NOT NULL,
  `score` decimal(5,1) DEFAULT NULL,
  `exam_id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `accessment_studentexamrecord_exam_id_6c764677_fk_ELW_unit_id` (`exam_id`),
  KEY `accessment_studentex_user_id_9e0c94d8_fk_Account_s` (`user_id`),
  CONSTRAINT `accessment_studentex_user_id_9e0c94d8_fk_Account_s` FOREIGN KEY (`user_id`) REFERENCES `account_students` (`id`),
  CONSTRAINT `accessment_studentexamrecord_exam_id_6c764677_fk_ELW_unit_id` FOREIGN KEY (`exam_id`) REFERENCES `elw_unit` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `accessment_studentexamrecord`
--

LOCK TABLES `accessment_studentexamrecord` WRITE;
/*!40000 ALTER TABLE `accessment_studentexamrecord` DISABLE KEYS */;
/*!40000 ALTER TABLE `accessment_studentexamrecord` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `accessment_studentmediaplayrecord`
--

DROP TABLE IF EXISTS `accessment_studentmediaplayrecord`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `accessment_studentmediaplayrecord` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `play_count` int NOT NULL,
  `last_pause_time` double NOT NULL,
  `main_question_id` bigint NOT NULL,
  `media_material_id` bigint DEFAULT NULL,
  `student_exam_record_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `accessment_studentmediap_student_exam_record_id_m_b51297f7_uniq` (`student_exam_record_id`,`main_question_id`,`media_material_id`),
  KEY `accessment_studentme_main_question_id_857c242e_fk_ELW_mainq` (`main_question_id`),
  KEY `accessment_studentme_media_material_id_c76bb13f_fk_ELW_media` (`media_material_id`),
  CONSTRAINT `accessment_studentme_main_question_id_857c242e_fk_ELW_mainq` FOREIGN KEY (`main_question_id`) REFERENCES `elw_mainquestion` (`id`),
  CONSTRAINT `accessment_studentme_media_material_id_c76bb13f_fk_ELW_media` FOREIGN KEY (`media_material_id`) REFERENCES `elw_mediamaterial` (`id`),
  CONSTRAINT `accessment_studentme_student_exam_record__42056cc1_fk_accessmen` FOREIGN KEY (`student_exam_record_id`) REFERENCES `accessment_studentexamrecord` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `accessment_studentmediaplayrecord`
--

LOCK TABLES `accessment_studentmediaplayrecord` WRITE;
/*!40000 ALTER TABLE `accessment_studentmediaplayrecord` DISABLE KEYS */;
/*!40000 ALTER TABLE `accessment_studentmediaplayrecord` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `accessment_studentpagerecord`
--

DROP TABLE IF EXISTS `accessment_studentpagerecord`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `accessment_studentpagerecord` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `submitted` tinyint(1) NOT NULL,
  `submitted_at` datetime(6) DEFAULT NULL,
  `is_expired` tinyint(1) NOT NULL,
  `remaining_time` double DEFAULT NULL,
  `late_score` decimal(2,1) NOT NULL,
  `page_score` decimal(5,1) NOT NULL,
  `feedback` longtext NOT NULL,
  `is_graded` tinyint(1) NOT NULL,
  `page_id` bigint NOT NULL,
  `student_exam_record_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `accessment_studentpa_page_id_5c72450d_fk_ELW_paper` (`page_id`),
  KEY `accessment_studentpa_student_exam_record__9d4bfd90_fk_accessmen` (`student_exam_record_id`),
  CONSTRAINT `accessment_studentpa_page_id_5c72450d_fk_ELW_paper` FOREIGN KEY (`page_id`) REFERENCES `elw_paperpage` (`id`),
  CONSTRAINT `accessment_studentpa_student_exam_record__9d4bfd90_fk_accessmen` FOREIGN KEY (`student_exam_record_id`) REFERENCES `accessment_studentexamrecord` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `accessment_studentpagerecord`
--

LOCK TABLES `accessment_studentpagerecord` WRITE;
/*!40000 ALTER TABLE `accessment_studentpagerecord` DISABLE KEYS */;
/*!40000 ALTER TABLE `accessment_studentpagerecord` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `account_admins`
--

DROP TABLE IF EXISTS `account_admins`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `account_admins` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `username` varchar(32) NOT NULL,
  `password` longtext NOT NULL,
  `user_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `Account_admins_user_id_34467d78_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `account_admins`
--

LOCK TABLES `account_admins` WRITE;
/*!40000 ALTER TABLE `account_admins` DISABLE KEYS */;
INSERT INTO `account_admins` VALUES (1,'admin','pbkdf2_sha256$600000$JDdXggBegqkwI4tVQkkV2w$KpoyGBAIDdPg/f1x7FqHIjyDIAQovujXXBd/9QaJr6c=',1);
/*!40000 ALTER TABLE `account_admins` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `account_attendance`
--

DROP TABLE IF EXISTS `account_attendance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `account_attendance` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `week` int NOT NULL,
  `status` varchar(20) NOT NULL,
  `added_class_time_id` bigint DEFAULT NULL,
  `adjusted_class_time_id` bigint DEFAULT NULL,
  `student_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `Account_attendance_added_class_time_id_e276850b_fk_Account_c` (`added_class_time_id`),
  KEY `Account_attendance_adjusted_class_time__ba609375_fk_Account_c` (`adjusted_class_time_id`),
  KEY `Account_attendance_student_id_930e03dd_fk_Account_students_id` (`student_id`),
  CONSTRAINT `Account_attendance_added_class_time_id_e276850b_fk_Account_c` FOREIGN KEY (`added_class_time_id`) REFERENCES `account_classscheduleaddition` (`id`),
  CONSTRAINT `Account_attendance_adjusted_class_time__ba609375_fk_Account_c` FOREIGN KEY (`adjusted_class_time_id`) REFERENCES `account_classscheduleadjustment` (`id`),
  CONSTRAINT `Account_attendance_student_id_930e03dd_fk_Account_students_id` FOREIGN KEY (`student_id`) REFERENCES `account_students` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `account_attendance`
--

LOCK TABLES `account_attendance` WRITE;
/*!40000 ALTER TABLE `account_attendance` DISABLE KEYS */;
/*!40000 ALTER TABLE `account_attendance` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `account_class`
--

DROP TABLE IF EXISTS `account_class`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `account_class` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `class_name` varchar(200) DEFAULT NULL,
  `start_date` varchar(20) DEFAULT NULL,
  `week` int NOT NULL,
  `start_time` varchar(50) NOT NULL,
  `end_time` varchar(50) NOT NULL,
  `course_id` bigint NOT NULL,
  `teacher_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `Account_class_course_id_03d59ef2_fk_Account_course_id` (`course_id`),
  KEY `Account_class_teacher_id_bbc8d03c_fk_Account_teachers_id` (`teacher_id`),
  CONSTRAINT `Account_class_course_id_03d59ef2_fk_Account_course_id` FOREIGN KEY (`course_id`) REFERENCES `account_course` (`id`),
  CONSTRAINT `Account_class_teacher_id_bbc8d03c_fk_Account_teachers_id` FOREIGN KEY (`teacher_id`) REFERENCES `account_teachers` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `account_class`
--

LOCK TABLES `account_class` WRITE;
/*!40000 ALTER TABLE `account_class` DISABLE KEYS */;
/*!40000 ALTER TABLE `account_class` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `account_classscheduleaddition`
--

DROP TABLE IF EXISTS `account_classscheduleaddition`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `account_classscheduleaddition` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `week` int NOT NULL,
  `weekday` int NOT NULL,
  `class_begin_time` varchar(50) NOT NULL,
  `class_end_time` varchar(50) NOT NULL,
  `class_instance_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `Account_classschedul_class_instance_id_809a26ff_fk_Account_c` (`class_instance_id`),
  CONSTRAINT `Account_classschedul_class_instance_id_809a26ff_fk_Account_c` FOREIGN KEY (`class_instance_id`) REFERENCES `account_class` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `account_classscheduleaddition`
--

LOCK TABLES `account_classscheduleaddition` WRITE;
/*!40000 ALTER TABLE `account_classscheduleaddition` DISABLE KEYS */;
/*!40000 ALTER TABLE `account_classscheduleaddition` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `account_classscheduleadjustment`
--

DROP TABLE IF EXISTS `account_classscheduleadjustment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `account_classscheduleadjustment` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `week` int NOT NULL,
  `new_week_day` int NOT NULL,
  `new_class_begin_time` varchar(50) NOT NULL,
  `new_class_end_time` varchar(50) NOT NULL,
  `class_instance_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `Account_classschedul_class_instance_id_812d1b8d_fk_Account_c` (`class_instance_id`),
  CONSTRAINT `Account_classschedul_class_instance_id_812d1b8d_fk_Account_c` FOREIGN KEY (`class_instance_id`) REFERENCES `account_class` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `account_classscheduleadjustment`
--

LOCK TABLES `account_classscheduleadjustment` WRITE;
/*!40000 ALTER TABLE `account_classscheduleadjustment` DISABLE KEYS */;
/*!40000 ALTER TABLE `account_classscheduleadjustment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `account_course`
--

DROP TABLE IF EXISTS `account_course`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `account_course` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `year` int NOT NULL,
  `grade` varchar(30) NOT NULL,
  `semester` varchar(30) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `account_course`
--

LOCK TABLES `account_course` WRITE;
/*!40000 ALTER TABLE `account_course` DISABLE KEYS */;
/*!40000 ALTER TABLE `account_course` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `account_students`
--

DROP TABLE IF EXISTS `account_students`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `account_students` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `username` varchar(20) NOT NULL,
  `name` varchar(20) NOT NULL,
  `password` varchar(100) NOT NULL,
  `seat_number` varchar(10) DEFAULT NULL,
  `class_instance_id` bigint NOT NULL,
  `user_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `user_id` (`user_id`),
  KEY `Account_students_class_instance_id_8ad00b4f_fk_Account_class_id` (`class_instance_id`),
  CONSTRAINT `Account_students_class_instance_id_8ad00b4f_fk_Account_class_id` FOREIGN KEY (`class_instance_id`) REFERENCES `account_class` (`id`),
  CONSTRAINT `Account_students_user_id_366707c5_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `account_students`
--

LOCK TABLES `account_students` WRITE;
/*!40000 ALTER TABLE `account_students` DISABLE KEYS */;
/*!40000 ALTER TABLE `account_students` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `account_teachers`
--

DROP TABLE IF EXISTS `account_teachers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `account_teachers` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `username` varchar(20) NOT NULL,
  `name` varchar(20) NOT NULL,
  `password` varchar(100) NOT NULL,
  `user_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `Account_teachers_user_id_094384a0_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `account_teachers`
--

LOCK TABLES `account_teachers` WRITE;
/*!40000 ALTER TABLE `account_teachers` DISABLE KEYS */;
/*!40000 ALTER TABLE `account_teachers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `announce_announcement`
--

DROP TABLE IF EXISTS `announce_announcement`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `announce_announcement` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `a_title` varchar(64) NOT NULL,
  `a_content` varchar(3000) DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `teachers_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `announce_announcemen_teachers_id_ae29ffc5_fk_Account_t` (`teachers_id`),
  CONSTRAINT `announce_announcemen_teachers_id_ae29ffc5_fk_Account_t` FOREIGN KEY (`teachers_id`) REFERENCES `account_teachers` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `announce_announcement`
--

LOCK TABLES `announce_announcement` WRITE;
/*!40000 ALTER TABLE `announce_announcement` DISABLE KEYS */;
/*!40000 ALTER TABLE `announce_announcement` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `announce_announcement_receivers`
--

DROP TABLE IF EXISTS `announce_announcement_receivers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `announce_announcement_receivers` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `announcement_id` bigint NOT NULL,
  `students_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `announce_announcement_re_announcement_id_students_ccf532fa_uniq` (`announcement_id`,`students_id`),
  KEY `announce_announcemen_students_id_62329957_fk_Account_s` (`students_id`),
  CONSTRAINT `announce_announcemen_announcement_id_b965d342_fk_announce_` FOREIGN KEY (`announcement_id`) REFERENCES `announce_announcement` (`id`),
  CONSTRAINT `announce_announcemen_students_id_62329957_fk_Account_s` FOREIGN KEY (`students_id`) REFERENCES `account_students` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `announce_announcement_receivers`
--

LOCK TABLES `announce_announcement_receivers` WRITE;
/*!40000 ALTER TABLE `announce_announcement_receivers` DISABLE KEYS */;
/*!40000 ALTER TABLE `announce_announcement_receivers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `announce_message`
--

DROP TABLE IF EXISTS `announce_message`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `announce_message` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `sender` varchar(100) NOT NULL,
  `receiver` varchar(100) NOT NULL,
  `content` longtext NOT NULL,
  `is_read` tinyint(1) NOT NULL,
  `read_at` datetime(6) DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `is_announcement` tinyint(1) NOT NULL,
  `announcement_id` bigint DEFAULT NULL,
  `post_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `announce_message_announcement_id_ff66e98f_fk_announce_` (`announcement_id`),
  KEY `announce_message_post_id_de17b416_fk_forum_post_id` (`post_id`),
  CONSTRAINT `announce_message_announcement_id_ff66e98f_fk_announce_` FOREIGN KEY (`announcement_id`) REFERENCES `announce_announcement` (`id`),
  CONSTRAINT `announce_message_post_id_de17b416_fk_forum_post_id` FOREIGN KEY (`post_id`) REFERENCES `forum_post` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `announce_message`
--

LOCK TABLES `announce_message` WRITE;
/*!40000 ALTER TABLE `announce_message` DISABLE KEYS */;
/*!40000 ALTER TABLE `announce_message` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
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

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
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

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=169 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can view log entry',1,'view_logentry'),(5,'Can add permission',2,'add_permission'),(6,'Can change permission',2,'change_permission'),(7,'Can delete permission',2,'delete_permission'),(8,'Can view permission',2,'view_permission'),(9,'Can add group',3,'add_group'),(10,'Can change group',3,'change_group'),(11,'Can delete group',3,'delete_group'),(12,'Can view group',3,'view_group'),(13,'Can add user',4,'add_user'),(14,'Can change user',4,'change_user'),(15,'Can delete user',4,'delete_user'),(16,'Can view user',4,'view_user'),(17,'Can add content type',5,'add_contenttype'),(18,'Can change content type',5,'change_contenttype'),(19,'Can delete content type',5,'delete_contenttype'),(20,'Can view content type',5,'view_contenttype'),(21,'Can add session',6,'add_session'),(22,'Can change session',6,'change_session'),(23,'Can delete session',6,'delete_session'),(24,'Can view session',6,'view_session'),(25,'Can add document',7,'add_document'),(26,'Can change document',7,'change_document'),(27,'Can delete document',7,'delete_document'),(28,'Can view document',7,'view_document'),(29,'Can add login info',8,'add_logininfo'),(30,'Can change login info',8,'change_logininfo'),(31,'Can delete login info',8,'delete_logininfo'),(32,'Can view login info',8,'view_logininfo'),(33,'Can add main question',9,'add_mainquestion'),(34,'Can change main question',9,'change_mainquestion'),(35,'Can delete main question',9,'delete_mainquestion'),(36,'Can view main question',9,'view_mainquestion'),(37,'Can add media material',10,'add_mediamaterial'),(38,'Can change media material',10,'change_mediamaterial'),(39,'Can delete media material',10,'delete_mediamaterial'),(40,'Can view media material',10,'view_mediamaterial'),(41,'Can add page main question',11,'add_pagemainquestion'),(42,'Can change page main question',11,'change_pagemainquestion'),(43,'Can delete page main question',11,'delete_pagemainquestion'),(44,'Can view page main question',11,'view_pagemainquestion'),(45,'Can add unit',12,'add_unit'),(46,'Can change unit',12,'change_unit'),(47,'Can delete unit',12,'delete_unit'),(48,'Can view unit',12,'view_unit'),(49,'Can add time management',13,'add_timemanagement'),(50,'Can change time management',13,'change_timemanagement'),(51,'Can delete time management',13,'delete_timemanagement'),(52,'Can view time management',13,'view_timemanagement'),(53,'Can add sub question',14,'add_subquestion'),(54,'Can change sub question',14,'change_subquestion'),(55,'Can delete sub question',14,'delete_subquestion'),(56,'Can view sub question',14,'view_subquestion'),(57,'Can add paper page',15,'add_paperpage'),(58,'Can change paper page',15,'change_paperpage'),(59,'Can delete paper page',15,'delete_paperpage'),(60,'Can view paper page',15,'view_paperpage'),(61,'Can add page sub question',16,'add_pagesubquestion'),(62,'Can change page sub question',16,'change_pagesubquestion'),(63,'Can delete page sub question',16,'delete_pagesubquestion'),(64,'Can view page sub question',16,'view_pagesubquestion'),(65,'Can add matching option',17,'add_matchingoption'),(66,'Can change matching option',17,'change_matchingoption'),(67,'Can delete matching option',17,'delete_matchingoption'),(68,'Can view matching option',17,'view_matchingoption'),(69,'Can add correction',18,'add_correction'),(70,'Can change correction',18,'change_correction'),(71,'Can delete correction',18,'delete_correction'),(72,'Can view correction',18,'view_correction'),(73,'Can add choice option',19,'add_choiceoption'),(74,'Can change choice option',19,'change_choiceoption'),(75,'Can delete choice option',19,'delete_choiceoption'),(76,'Can view choice option',19,'view_choiceoption'),(77,'Can add blank',20,'add_blank'),(78,'Can change blank',20,'change_blank'),(79,'Can delete blank',20,'delete_blank'),(80,'Can view blank',20,'view_blank'),(81,'Can add post',21,'add_post'),(82,'Can change post',21,'change_post'),(83,'Can delete post',21,'delete_post'),(84,'Can view post',21,'view_post'),(85,'Can add comment',22,'add_comment'),(86,'Can change comment',22,'change_comment'),(87,'Can delete comment',22,'delete_comment'),(88,'Can view comment',22,'view_comment'),(89,'Can add anonymous',23,'add_anonymous'),(90,'Can change anonymous',23,'change_anonymous'),(91,'Can delete anonymous',23,'delete_anonymous'),(92,'Can view anonymous',23,'view_anonymous'),(93,'Can add announcement',24,'add_announcement'),(94,'Can change announcement',24,'change_announcement'),(95,'Can delete announcement',24,'delete_announcement'),(96,'Can view announcement',24,'view_announcement'),(97,'Can add message',25,'add_message'),(98,'Can change message',25,'change_message'),(99,'Can delete message',25,'delete_message'),(100,'Can view message',25,'view_message'),(101,'Can add student exam record',26,'add_studentexamrecord'),(102,'Can change student exam record',26,'change_studentexamrecord'),(103,'Can delete student exam record',26,'delete_studentexamrecord'),(104,'Can view student exam record',26,'view_studentexamrecord'),(105,'Can add student page record',27,'add_studentpagerecord'),(106,'Can change student page record',27,'change_studentpagerecord'),(107,'Can delete student page record',27,'delete_studentpagerecord'),(108,'Can view student page record',27,'view_studentpagerecord'),(109,'Can add student answer',28,'add_studentanswer'),(110,'Can change student answer',28,'change_studentanswer'),(111,'Can delete student answer',28,'delete_studentanswer'),(112,'Can view student answer',28,'view_studentanswer'),(113,'Can add student media play record',29,'add_studentmediaplayrecord'),(114,'Can change student media play record',29,'change_studentmediaplayrecord'),(115,'Can delete student media play record',29,'delete_studentmediaplayrecord'),(116,'Can view student media play record',29,'view_studentmediaplayrecord'),(117,'Can add class',30,'add_class'),(118,'Can change class',30,'change_class'),(119,'Can delete class',30,'delete_class'),(120,'Can view class',30,'view_class'),(121,'Can add course',31,'add_course'),(122,'Can change course',31,'change_course'),(123,'Can delete course',31,'delete_course'),(124,'Can view course',31,'view_course'),(125,'Can add teachers',32,'add_teachers'),(126,'Can change teachers',32,'change_teachers'),(127,'Can delete teachers',32,'delete_teachers'),(128,'Can view teachers',32,'view_teachers'),(129,'Can add students',33,'add_students'),(130,'Can change students',33,'change_students'),(131,'Can delete students',33,'delete_students'),(132,'Can view students',33,'view_students'),(133,'Can add class schedule adjustment',34,'add_classscheduleadjustment'),(134,'Can change class schedule adjustment',34,'change_classscheduleadjustment'),(135,'Can delete class schedule adjustment',34,'delete_classscheduleadjustment'),(136,'Can view class schedule adjustment',34,'view_classscheduleadjustment'),(137,'Can add class schedule addition',35,'add_classscheduleaddition'),(138,'Can change class schedule addition',35,'change_classscheduleaddition'),(139,'Can delete class schedule addition',35,'delete_classscheduleaddition'),(140,'Can view class schedule addition',35,'view_classscheduleaddition'),(141,'Can add attendance',36,'add_attendance'),(142,'Can change attendance',36,'change_attendance'),(143,'Can delete attendance',36,'delete_attendance'),(144,'Can view attendance',36,'view_attendance'),(145,'Can add admins',37,'add_admins'),(146,'Can change admins',37,'change_admins'),(147,'Can delete admins',37,'delete_admins'),(148,'Can view admins',37,'view_admins'),(149,'Can add backup database',38,'add_backupdatabase'),(150,'Can change backup database',38,'change_backupdatabase'),(151,'Can delete backup database',38,'delete_backupdatabase'),(152,'Can view backup database',38,'view_backupdatabase'),(153,'Can add log entry',39,'add_logentry'),(154,'Can change log entry',39,'change_logentry'),(155,'Can delete log entry',39,'delete_logentry'),(156,'Can view log entry',39,'view_logentry'),(157,'Can add classroom layout',40,'add_classroomlayout'),(158,'Can change classroom layout',40,'change_classroomlayout'),(159,'Can delete classroom layout',40,'delete_classroomlayout'),(160,'Can view classroom layout',40,'view_classroomlayout'),(161,'Can add 逾期扣分规则',41,'add_overduedeductionrule'),(162,'Can change 逾期扣分规则',41,'change_overduedeductionrule'),(163,'Can delete 逾期扣分规则',41,'delete_overduedeductionrule'),(164,'Can view 逾期扣分规则',41,'view_overduedeductionrule'),(165,'Can add 逾期时间段',42,'add_overdueperiod'),(166,'Can change 逾期时间段',42,'change_overdueperiod'),(167,'Can delete 逾期时间段',42,'delete_overdueperiod'),(168,'Can view 逾期时间段',42,'view_overdueperiod');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user`
--

LOCK TABLES `auth_user` WRITE;
/*!40000 ALTER TABLE `auth_user` DISABLE KEYS */;
INSERT INTO `auth_user` VALUES (1,'pbkdf2_sha256$600000$JDdXggBegqkwI4tVQkkV2w$KpoyGBAIDdPg/f1x7FqHIjyDIAQovujXXBd/9QaJr6c=','2025-04-24 22:25:21.529617',1,'admin','','','',1,1,'2025-04-24 22:24:04.376748');
/*!40000 ALTER TABLE `auth_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_groups`
--

DROP TABLE IF EXISTS `auth_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user_groups` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`),
  CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_groups`
--

LOCK TABLES `auth_user_groups` WRITE;
/*!40000 ALTER TABLE `auth_user_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_user_permissions`
--

DROP TABLE IF EXISTS `auth_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user_user_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_user_permissions`
--

LOCK TABLES `auth_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `auth_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `backup_backupdatabase`
--

DROP TABLE IF EXISTS `backup_backupdatabase`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `backup_backupdatabase` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `operation` varchar(10) NOT NULL,
  `status` varchar(20) NOT NULL,
  `backup_to` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `backup_backupdatabase`
--

LOCK TABLES `backup_backupdatabase` WRITE;
/*!40000 ALTER TABLE `backup_backupdatabase` DISABLE KEYS */;
INSERT INTO `backup_backupdatabase` VALUES (1,'2025-04-24 22:25:31.443872','backup','in_progress','');
/*!40000 ALTER TABLE `backup_backupdatabase` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `django_admin_log_chk_1` CHECK ((`action_flag` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
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

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=43 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (28,'accessment','studentanswer'),(26,'accessment','studentexamrecord'),(29,'accessment','studentmediaplayrecord'),(27,'accessment','studentpagerecord'),(37,'Account','admins'),(36,'Account','attendance'),(30,'Account','class'),(35,'Account','classscheduleaddition'),(34,'Account','classscheduleadjustment'),(31,'Account','course'),(33,'Account','students'),(32,'Account','teachers'),(1,'admin','logentry'),(24,'announce','announcement'),(25,'announce','message'),(3,'auth','group'),(2,'auth','permission'),(4,'auth','user'),(38,'Backup','backupdatabase'),(5,'contenttypes','contenttype'),(20,'ELW','blank'),(19,'ELW','choiceoption'),(18,'ELW','correction'),(7,'ELW','document'),(8,'ELW','logininfo'),(9,'ELW','mainquestion'),(17,'ELW','matchingoption'),(10,'ELW','mediamaterial'),(11,'ELW','pagemainquestion'),(16,'ELW','pagesubquestion'),(15,'ELW','paperpage'),(14,'ELW','subquestion'),(13,'ELW','timemanagement'),(12,'ELW','unit'),(23,'forum','anonymous'),(22,'forum','comment'),(21,'forum','post'),(39,'Log','logentry'),(40,'Query','classroomlayout'),(41,'Query','overduedeductionrule'),(42,'Query','overdueperiod'),(6,'sessions','session');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2025-04-24 22:23:25.224130'),(2,'auth','0001_initial','2025-04-24 22:23:27.200515'),(3,'Account','0001_initial','2025-04-24 22:23:29.324995'),(4,'Backup','0001_initial','2025-04-24 22:23:29.396044'),(5,'Query','0001_initial','2025-04-24 22:23:30.024560'),(6,'ELW','0001_initial','2025-04-24 22:23:33.293661'),(7,'Log','0001_initial','2025-04-24 22:23:33.505195'),(8,'accessment','0001_initial','2025-04-24 22:23:35.208238'),(9,'admin','0001_initial','2025-04-24 22:23:35.635735'),(10,'admin','0002_logentry_remove_auto_add','2025-04-24 22:23:35.651563'),(11,'admin','0003_logentry_add_action_flag_choices','2025-04-24 22:23:35.672044'),(12,'forum','0001_initial','2025-04-24 22:23:37.803136'),(13,'announce','0001_initial','2025-04-24 22:23:38.820115'),(14,'contenttypes','0002_remove_content_type_name','2025-04-24 22:23:39.006584'),(15,'auth','0002_alter_permission_name_max_length','2025-04-24 22:23:39.171206'),(16,'auth','0003_alter_user_email_max_length','2025-04-24 22:23:39.356574'),(17,'auth','0004_alter_user_username_opts','2025-04-24 22:23:39.371059'),(18,'auth','0005_alter_user_last_login_null','2025-04-24 22:23:39.507737'),(19,'auth','0006_require_contenttypes_0002','2025-04-24 22:23:39.520153'),(20,'auth','0007_alter_validators_add_error_messages','2025-04-24 22:23:39.536196'),(21,'auth','0008_alter_user_username_max_length','2025-04-24 22:23:39.699350'),(22,'auth','0009_alter_user_last_name_max_length','2025-04-24 22:23:39.857595'),(23,'auth','0010_alter_group_name_max_length','2025-04-24 22:23:40.011223'),(24,'auth','0011_update_proxy_permissions','2025-04-24 22:23:40.039831'),(25,'auth','0012_alter_user_first_name_max_length','2025-04-24 22:23:40.189760'),(26,'sessions','0001_initial','2025-04-24 22:23:40.279939');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
INSERT INTO `django_session` VALUES ('5iwbasp0neforyjfy8kbb9bn6afj5os8','.eJzFV0uPmzAQ_isrzkkwxuaRW3tub-2pWUXjBwktgQpMpWqV_14PRNWu4zyWZJWTwfNpxt8342F4CSrozBqkKf_otSl3OlgGlFA-J2xO2TdKl5Qvo3jBkyjKSTAL2qZCDKhdWdvXvtNtDbvXW2W3rpqNfVyattezYA292a4RuC6VxUXBmz0B8peu0aB-Qr1pFrKpTVuKBUIWB2u3-NooXX0-YN842EK3RbdCZqQAYIpDpAVPWcSZsI-SCpYomfKcKw1FrouEJIoIRTMGTGgFeZJQgU53uu476-vHyypAVqtg-bQKVque5yS1C9OFsktq3eLCSLIKZhZR2jOP2ALapwLmsmxlpUfjDk_eofnIbcJTgkucaAyi89iJddl731ajLRz0D1Gi_ncohkWBAQGdDkcsKPV9hNd9VeGOaDUo2fY74T_gVN772dOdue6f0axLhdaIEOpuRN6YmmOUQqV3TRuTKAcruHSCvD9fX5pNaK-LtjX_d3KapvL0STaRm5sO5m7EnmCZADYsEg_MWTbEjLMMl5TFxzE7jNltS12pOVTmYqo4tSJYLbRkJ5xhD-nmstn484N9Jty0jb1TbnZ8GGs94C7l7A7cPYq-i6-bosRXD5QN1zYlOZ5WUXTP4-JUPaD7M0qieXKZf4xk0xi62qXuBvfV--g8ofFd-xEXyZB0HhVXMTjXjz5J2fS1CTvTK9uUutNVf4R8R-1P1MFX8BO5u-nKvZ8Png_fKpLdTVejQW7tDbys63_kQ3Sdyt3RNSIe32msh3FCwy1KSju6XiHjCHuIhtfzdFXzDTOvj4Ldj9-vKIe3K7Q84B4j5m30XYWprz3bKWX4hurxMyPIMPtwfou0xtg_Fqjl8RB-DvsQiafyd7X1j3oFzv0pEHHLnW_61vM7cwr3GBWvZurqdjQzZ_vnYP8Phg3bCw:1u7xVx:7yw5WPy87B1Iy9k_wz_SAM1WuMYS2klXje81FkVhDT4','2025-04-24 22:55:21.756110');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `elw_blank`
--

DROP TABLE IF EXISTS `elw_blank`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `elw_blank` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `index` int NOT NULL,
  `sub_question_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ELW_blank_sub_question_id_ac07232c_fk_ELW_subquestion_id` (`sub_question_id`),
  CONSTRAINT `ELW_blank_sub_question_id_ac07232c_fk_ELW_subquestion_id` FOREIGN KEY (`sub_question_id`) REFERENCES `elw_subquestion` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `elw_blank`
--

LOCK TABLES `elw_blank` WRITE;
/*!40000 ALTER TABLE `elw_blank` DISABLE KEYS */;
/*!40000 ALTER TABLE `elw_blank` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `elw_choiceoption`
--

DROP TABLE IF EXISTS `elw_choiceoption`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `elw_choiceoption` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `option_label` varchar(1) NOT NULL,
  `option_content` longtext,
  `image_url` varchar(10000) DEFAULT NULL,
  `is_answer` tinyint(1) NOT NULL,
  `sub_question_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ELW_choiceoption_sub_question_id_da20ae07_fk_ELW_subquestion_id` (`sub_question_id`),
  CONSTRAINT `ELW_choiceoption_sub_question_id_da20ae07_fk_ELW_subquestion_id` FOREIGN KEY (`sub_question_id`) REFERENCES `elw_subquestion` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `elw_choiceoption`
--

LOCK TABLES `elw_choiceoption` WRITE;
/*!40000 ALTER TABLE `elw_choiceoption` DISABLE KEYS */;
/*!40000 ALTER TABLE `elw_choiceoption` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `elw_correction`
--

DROP TABLE IF EXISTS `elw_correction`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `elw_correction` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `type` varchar(10) NOT NULL,
  `index` int NOT NULL,
  `sub_question_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ELW_correction_sub_question_id_6b6ec044_fk_ELW_subquestion_id` (`sub_question_id`),
  CONSTRAINT `ELW_correction_sub_question_id_6b6ec044_fk_ELW_subquestion_id` FOREIGN KEY (`sub_question_id`) REFERENCES `elw_subquestion` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `elw_correction`
--

LOCK TABLES `elw_correction` WRITE;
/*!40000 ALTER TABLE `elw_correction` DISABLE KEYS */;
/*!40000 ALTER TABLE `elw_correction` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `elw_document`
--

DROP TABLE IF EXISTS `elw_document`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `elw_document` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `uploaded_at` datetime(6) NOT NULL,
  `document_url` varchar(100) NOT NULL,
  `content` longtext NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `elw_document`
--

LOCK TABLES `elw_document` WRITE;
/*!40000 ALTER TABLE `elw_document` DISABLE KEYS */;
/*!40000 ALTER TABLE `elw_document` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `elw_logininfo`
--

DROP TABLE IF EXISTS `elw_logininfo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `elw_logininfo` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `username` varchar(20) NOT NULL,
  `week` int NOT NULL,
  `action` varchar(20) NOT NULL,
  `action_time` datetime(6) NOT NULL,
  `last_active_time` varchar(50) NOT NULL,
  `device_info` varchar(500) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `elw_logininfo`
--

LOCK TABLES `elw_logininfo` WRITE;
/*!40000 ALTER TABLE `elw_logininfo` DISABLE KEYS */;
/*!40000 ALTER TABLE `elw_logininfo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `elw_mainquestion`
--

DROP TABLE IF EXISTS `elw_mainquestion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `elw_mainquestion` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `question_type` varchar(20) NOT NULL,
  `question_text` longtext NOT NULL,
  `image_url` varchar(10000) DEFAULT NULL,
  `maximum_play` int NOT NULL,
  `minimum_play` int NOT NULL,
  `start_time` time(6) DEFAULT NULL,
  `end_time` time(6) DEFAULT NULL,
  `allow_pause` tinyint(1) DEFAULT NULL,
  `limited_time` time(6) DEFAULT NULL,
  `no_media` tinyint(1) DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `media_material_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ELW_mainquestion_media_material_id_3fcfcc30_fk_ELW_media` (`media_material_id`),
  CONSTRAINT `ELW_mainquestion_media_material_id_3fcfcc30_fk_ELW_media` FOREIGN KEY (`media_material_id`) REFERENCES `elw_mediamaterial` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `elw_mainquestion`
--

LOCK TABLES `elw_mainquestion` WRITE;
/*!40000 ALTER TABLE `elw_mainquestion` DISABLE KEYS */;
/*!40000 ALTER TABLE `elw_mainquestion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `elw_matchingoption`
--

DROP TABLE IF EXISTS `elw_matchingoption`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `elw_matchingoption` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `option_label` varchar(1) NOT NULL,
  `option_content` longtext,
  `image_url` varchar(10000) DEFAULT NULL,
  `sub_question_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ELW_matchingoption_sub_question_id_fbcbf4e7_fk_ELW_subqu` (`sub_question_id`),
  CONSTRAINT `ELW_matchingoption_sub_question_id_fbcbf4e7_fk_ELW_subqu` FOREIGN KEY (`sub_question_id`) REFERENCES `elw_subquestion` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `elw_matchingoption`
--

LOCK TABLES `elw_matchingoption` WRITE;
/*!40000 ALTER TABLE `elw_matchingoption` DISABLE KEYS */;
/*!40000 ALTER TABLE `elw_matchingoption` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `elw_mediamaterial`
--

DROP TABLE IF EXISTS `elw_mediamaterial`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `elw_mediamaterial` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `title` longtext NOT NULL,
  `theme` varchar(50) NOT NULL,
  `abstract` longtext NOT NULL,
  `keywords` longtext NOT NULL,
  `transcript` longtext NOT NULL,
  `media_url` varchar(100) NOT NULL,
  `image_url` varchar(10000) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `elw_mediamaterial`
--

LOCK TABLES `elw_mediamaterial` WRITE;
/*!40000 ALTER TABLE `elw_mediamaterial` DISABLE KEYS */;
/*!40000 ALTER TABLE `elw_mediamaterial` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `elw_pagemainquestion`
--

DROP TABLE IF EXISTS `elw_pagemainquestion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `elw_pagemainquestion` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `main_question_id` bigint NOT NULL,
  `page_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ELW_pagemainquestion_page_id_de1212bb_fk_ELW_paperpage_id` (`page_id`),
  KEY `ELW_pagemainquestion_main_question_id_969c1395_fk_ELW_mainq` (`main_question_id`),
  CONSTRAINT `ELW_pagemainquestion_main_question_id_969c1395_fk_ELW_mainq` FOREIGN KEY (`main_question_id`) REFERENCES `elw_mainquestion` (`id`),
  CONSTRAINT `ELW_pagemainquestion_page_id_de1212bb_fk_ELW_paperpage_id` FOREIGN KEY (`page_id`) REFERENCES `elw_paperpage` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `elw_pagemainquestion`
--

LOCK TABLES `elw_pagemainquestion` WRITE;
/*!40000 ALTER TABLE `elw_pagemainquestion` DISABLE KEYS */;
/*!40000 ALTER TABLE `elw_pagemainquestion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `elw_pagesubquestion`
--

DROP TABLE IF EXISTS `elw_pagesubquestion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `elw_pagesubquestion` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `page_main_question_id` bigint NOT NULL,
  `sub_question_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ELW_pagesubquestion_page_main_question_i_0b7d9f3d_fk_ELW_pagem` (`page_main_question_id`),
  KEY `ELW_pagesubquestion_sub_question_id_8427363a_fk_ELW_subqu` (`sub_question_id`),
  CONSTRAINT `ELW_pagesubquestion_page_main_question_i_0b7d9f3d_fk_ELW_pagem` FOREIGN KEY (`page_main_question_id`) REFERENCES `elw_pagemainquestion` (`id`),
  CONSTRAINT `ELW_pagesubquestion_sub_question_id_8427363a_fk_ELW_subqu` FOREIGN KEY (`sub_question_id`) REFERENCES `elw_subquestion` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `elw_pagesubquestion`
--

LOCK TABLES `elw_pagesubquestion` WRITE;
/*!40000 ALTER TABLE `elw_pagesubquestion` DISABLE KEYS */;
/*!40000 ALTER TABLE `elw_pagesubquestion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `elw_paperpage`
--

DROP TABLE IF EXISTS `elw_paperpage`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `elw_paperpage` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `order` int NOT NULL,
  `text` longtext,
  `limited_time` int DEFAULT NULL,
  `can_modify` tinyint(1) DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `unit_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ELW_paperpage_unit_id_087d81d0_fk_ELW_unit_id` (`unit_id`),
  CONSTRAINT `ELW_paperpage_unit_id_087d81d0_fk_ELW_unit_id` FOREIGN KEY (`unit_id`) REFERENCES `elw_unit` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `elw_paperpage`
--

LOCK TABLES `elw_paperpage` WRITE;
/*!40000 ALTER TABLE `elw_paperpage` DISABLE KEYS */;
/*!40000 ALTER TABLE `elw_paperpage` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `elw_subquestion`
--

DROP TABLE IF EXISTS `elw_subquestion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `elw_subquestion` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `question_text` longtext NOT NULL,
  `image_url` varchar(10000) DEFAULT NULL,
  `tips` longtext,
  `answer` longtext NOT NULL,
  `analysis` longtext,
  `score` double NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `main_question_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ELW_subquestion_main_question_id_e5fd1c57_fk_ELW_mainquestion_id` (`main_question_id`),
  CONSTRAINT `ELW_subquestion_main_question_id_e5fd1c57_fk_ELW_mainquestion_id` FOREIGN KEY (`main_question_id`) REFERENCES `elw_mainquestion` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `elw_subquestion`
--

LOCK TABLES `elw_subquestion` WRITE;
/*!40000 ALTER TABLE `elw_subquestion` DISABLE KEYS */;
/*!40000 ALTER TABLE `elw_subquestion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `elw_timemanagement`
--

DROP TABLE IF EXISTS `elw_timemanagement`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `elw_timemanagement` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `week` int NOT NULL,
  `exam_date` date DEFAULT NULL,
  `start_time` time(6) DEFAULT NULL,
  `end_time` time(6) DEFAULT NULL,
  `duration` int DEFAULT NULL,
  `unit_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ELW_timemanagement_unit_id_613c9c72_fk_ELW_unit_id` (`unit_id`),
  CONSTRAINT `ELW_timemanagement_unit_id_613c9c72_fk_ELW_unit_id` FOREIGN KEY (`unit_id`) REFERENCES `elw_unit` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `elw_timemanagement`
--

LOCK TABLES `elw_timemanagement` WRITE;
/*!40000 ALTER TABLE `elw_timemanagement` DISABLE KEYS */;
/*!40000 ALTER TABLE `elw_timemanagement` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `elw_unit`
--

DROP TABLE IF EXISTS `elw_unit`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `elw_unit` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `order` int NOT NULL,
  `title` varchar(100) DEFAULT NULL,
  `type` varchar(20) NOT NULL,
  `class_instance_id` bigint NOT NULL,
  `overdue_rule_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ELW_unit_class_instance_id_11092f6d_fk_Account_class_id` (`class_instance_id`),
  KEY `ELW_unit_overdue_rule_id_05bd8b5a_fk_Query_ove` (`overdue_rule_id`),
  CONSTRAINT `ELW_unit_class_instance_id_11092f6d_fk_Account_class_id` FOREIGN KEY (`class_instance_id`) REFERENCES `account_class` (`id`),
  CONSTRAINT `ELW_unit_overdue_rule_id_05bd8b5a_fk_Query_ove` FOREIGN KEY (`overdue_rule_id`) REFERENCES `query_overduedeductionrule` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `elw_unit`
--

LOCK TABLES `elw_unit` WRITE;
/*!40000 ALTER TABLE `elw_unit` DISABLE KEYS */;
/*!40000 ALTER TABLE `elw_unit` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `forum_anonymous`
--

DROP TABLE IF EXISTS `forum_anonymous`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `forum_anonymous` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `anonymous_name` varchar(50) NOT NULL,
  `post_id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `forum_anonymous_user_id_post_id_c9f1b705_uniq` (`user_id`,`post_id`),
  KEY `forum_anonymous_post_id_6f21fda2_fk_forum_post_id` (`post_id`),
  CONSTRAINT `forum_anonymous_post_id_6f21fda2_fk_forum_post_id` FOREIGN KEY (`post_id`) REFERENCES `forum_post` (`id`),
  CONSTRAINT `forum_anonymous_user_id_c6525759_fk_Account_students_id` FOREIGN KEY (`user_id`) REFERENCES `account_students` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `forum_anonymous`
--

LOCK TABLES `forum_anonymous` WRITE;
/*!40000 ALTER TABLE `forum_anonymous` DISABLE KEYS */;
/*!40000 ALTER TABLE `forum_anonymous` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `forum_comment`
--

DROP TABLE IF EXISTS `forum_comment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `forum_comment` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `content` longtext NOT NULL,
  `is_top` tinyint(1) NOT NULL,
  `is_marked` tinyint(1) NOT NULL,
  `author` varchar(100) DEFAULT NULL,
  `is_anonymous` tinyint(1) NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `anonymous_name` varchar(100) DEFAULT NULL,
  `parent_comment_id` bigint DEFAULT NULL,
  `post_id` bigint NOT NULL,
  `student_id` bigint DEFAULT NULL,
  `teacher_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `forum_comment_parent_comment_id_c49a32c4_fk_forum_comment_id` (`parent_comment_id`),
  KEY `forum_comment_post_id_eb329692_fk_forum_post_id` (`post_id`),
  KEY `forum_comment_student_id_7f6b834e_fk_Account_students_id` (`student_id`),
  KEY `forum_comment_teacher_id_42b6a22c_fk_Account_teachers_id` (`teacher_id`),
  CONSTRAINT `forum_comment_parent_comment_id_c49a32c4_fk_forum_comment_id` FOREIGN KEY (`parent_comment_id`) REFERENCES `forum_comment` (`id`),
  CONSTRAINT `forum_comment_post_id_eb329692_fk_forum_post_id` FOREIGN KEY (`post_id`) REFERENCES `forum_post` (`id`),
  CONSTRAINT `forum_comment_student_id_7f6b834e_fk_Account_students_id` FOREIGN KEY (`student_id`) REFERENCES `account_students` (`id`),
  CONSTRAINT `forum_comment_teacher_id_42b6a22c_fk_Account_teachers_id` FOREIGN KEY (`teacher_id`) REFERENCES `account_teachers` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `forum_comment`
--

LOCK TABLES `forum_comment` WRITE;
/*!40000 ALTER TABLE `forum_comment` DISABLE KEYS */;
/*!40000 ALTER TABLE `forum_comment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `forum_post`
--

DROP TABLE IF EXISTS `forum_post`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `forum_post` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `title` varchar(200) NOT NULL,
  `content` longtext NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `is_top` tinyint(1) NOT NULL,
  `top_score` int NOT NULL,
  `is_question` tinyint(1) NOT NULL,
  `is_public` tinyint(1) NOT NULL,
  `author` varchar(100) DEFAULT NULL,
  `is_anonymous` tinyint(1) NOT NULL,
  `anonymous_name` varchar(100) DEFAULT NULL,
  `name` varchar(100) DEFAULT NULL,
  `is_announcement` tinyint(1) NOT NULL,
  `main_question_id` bigint DEFAULT NULL,
  `student_id` bigint DEFAULT NULL,
  `sub_question_id` bigint DEFAULT NULL,
  `teacher_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `forum_post_main_question_id_db8ef12d_fk_ELW_mainquestion_id` (`main_question_id`),
  KEY `forum_post_student_id_62fb2e3f_fk_Account_students_id` (`student_id`),
  KEY `forum_post_sub_question_id_205516ba_fk_ELW_subquestion_id` (`sub_question_id`),
  KEY `forum_post_teacher_id_11e6e5dc_fk_Account_teachers_id` (`teacher_id`),
  CONSTRAINT `forum_post_main_question_id_db8ef12d_fk_ELW_mainquestion_id` FOREIGN KEY (`main_question_id`) REFERENCES `elw_mainquestion` (`id`),
  CONSTRAINT `forum_post_student_id_62fb2e3f_fk_Account_students_id` FOREIGN KEY (`student_id`) REFERENCES `account_students` (`id`),
  CONSTRAINT `forum_post_sub_question_id_205516ba_fk_ELW_subquestion_id` FOREIGN KEY (`sub_question_id`) REFERENCES `elw_subquestion` (`id`),
  CONSTRAINT `forum_post_teacher_id_11e6e5dc_fk_Account_teachers_id` FOREIGN KEY (`teacher_id`) REFERENCES `account_teachers` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `forum_post`
--

LOCK TABLES `forum_post` WRITE;
/*!40000 ALTER TABLE `forum_post` DISABLE KEYS */;
/*!40000 ALTER TABLE `forum_post` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `log_logentry`
--

DROP TABLE IF EXISTS `log_logentry`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `log_logentry` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `log_type` varchar(20) NOT NULL,
  `message` longtext NOT NULL,
  `operation_time` datetime(6) NOT NULL,
  `status` varchar(20) NOT NULL,
  `module` varchar(100) DEFAULT NULL,
  `user_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `Log_logentry_user_id_cbb474ab_fk_auth_user_id` (`user_id`),
  CONSTRAINT `Log_logentry_user_id_cbb474ab_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `log_logentry`
--

LOCK TABLES `log_logentry` WRITE;
/*!40000 ALTER TABLE `log_logentry` DISABLE KEYS */;
/*!40000 ALTER TABLE `log_logentry` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `query_classroomlayout`
--

DROP TABLE IF EXISTS `query_classroomlayout`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `query_classroomlayout` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `seat_rows` int DEFAULT NULL,
  `seat_cols` int DEFAULT NULL,
  `class_instance_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `Query_classroomlayou_class_instance_id_76c7d714_fk_Account_c` (`class_instance_id`),
  CONSTRAINT `Query_classroomlayou_class_instance_id_76c7d714_fk_Account_c` FOREIGN KEY (`class_instance_id`) REFERENCES `account_class` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `query_classroomlayout`
--

LOCK TABLES `query_classroomlayout` WRITE;
/*!40000 ALTER TABLE `query_classroomlayout` DISABLE KEYS */;
/*!40000 ALTER TABLE `query_classroomlayout` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `query_overduedeductionrule`
--

DROP TABLE IF EXISTS `query_overduedeductionrule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `query_overduedeductionrule` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `rule_name` varchar(100) NOT NULL,
  `description` longtext NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `is_default` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `rule_name` (`rule_name`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `query_overduedeductionrule`
--

LOCK TABLES `query_overduedeductionrule` WRITE;
/*!40000 ALTER TABLE `query_overduedeductionrule` DISABLE KEYS */;
INSERT INTO `query_overduedeductionrule` VALUES (1,'默认逾期扣分规则','默认规则：每超期一周增扣10%，最多扣100%',1,'2025-04-24 22:23:40.616704','2025-04-24 22:23:40.616704',1);
/*!40000 ALTER TABLE `query_overduedeductionrule` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `query_overdueperiod`
--

DROP TABLE IF EXISTS `query_overdueperiod`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `query_overdueperiod` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `period_name` varchar(50) NOT NULL,
  `min_days` int NOT NULL,
  `max_days` int DEFAULT NULL,
  `deduction_rate` decimal(3,2) NOT NULL,
  `description` longtext NOT NULL,
  `rule_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `Query_overdueperiod_rule_id_b8f179b2_fk_Query_ove` (`rule_id`),
  CONSTRAINT `Query_overdueperiod_rule_id_b8f179b2_fk_Query_ove` FOREIGN KEY (`rule_id`) REFERENCES `query_overduedeductionrule` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `query_overdueperiod`
--

LOCK TABLES `query_overdueperiod` WRITE;
/*!40000 ALTER TABLE `query_overdueperiod` DISABLE KEYS */;
INSERT INTO `query_overdueperiod` VALUES (1,'超期第1周',0,7,0.90,'超期1周，扣分10%',1),(2,'超期第2周',7,14,0.80,'超期2周，扣分20%',1),(3,'超期第3周',14,21,0.70,'超期3周，扣分30%',1),(4,'超期第4周',21,28,0.60,'超期4周，扣分40%',1),(5,'超期第5周',28,35,0.50,'超期5周，扣分50%',1),(6,'超期第6周',35,42,0.40,'超期6周，扣分60%',1),(7,'超期第7周',42,49,0.30,'超期7周，扣分70%',1),(8,'超期第8周',49,56,0.20,'超期8周，扣分80%',1),(9,'超期第9周',56,63,0.10,'超期9周，扣分90%',1),(10,'超期第10周',63,NULL,0.00,'超期10周，扣分100%',1);
/*!40000 ALTER TABLE `query_overdueperiod` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-04-24 22:25:33
