CREATE DATABASE IF NOT EXISTS `flaskylearn`;
USE `flaskylearn`;

CREATE TABLE IF NOT EXISTS `Contributor` (
  `email` varchar(64) PRIMARY KEY,
  `name` varchar(255) DEFAULT null,
  `surname` varchar(64) DEFAULT null,
  `password` varchar(64) DEFAULT null
);

CREATE TABLE IF NOT EXISTS `Video` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `description` text DEFAULT null,
  `path` varchar(255) DEFAULT null
);

CREATE TABLE IF NOT EXISTS `Course` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `name` varchar(255) DEFAULT null,
  `description` text DEFAULT null,
  `duration` int  UNSIGNED DEFAULT null
);

CREATE TABLE IF NOT EXISTS `Student` (
  `email` varchar(64) PRIMARY KEY,
  `name` varchar(255) DEFAULT null,
  `surname` varchar(255) DEFAULT null,
  `password` varchar(64) DEFAULT null
);

CREATE TABLE IF NOT EXISTS `Release` (
  `email` varchar(64),
  `id` int, 
  `timestamp` timestamp, 
  PRIMARY KEY (`email`, `id`)
);

CREATE TABLE IF NOT EXISTS `Composition` (
  `videoid` int,
  `courseid` int,
  `lesson` int DEFAULT null,
  PRIMARY KEY (`videoid`, `courseid`)
);

CREATE TABLE IF NOT EXISTS `Enrollment` (
  `email` varchar(64),
  `id` int,
  `timestamp` timestamp,
  PRIMARY KEY (`email`, `id`)
);

CREATE TABLE IF NOT EXISTS `Visualization` (
  `email` varchar(64),
  `id` int,
  `timestamp` timestamp,
  PRIMARY KEY (`email`, `id`, `timestamp`)
);

CREATE TABLE IF NOT EXISTS `Test` (
  `courseid` int,
  `question` int,
  `weight` float DEFAULT 1,
  PRIMARY KEY(`courseid`, `question`)
);

CREATE TABLE IF NOT EXISTS `Question` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `topic` text DEFAULT null
);

CREATE TABLE IF NOT EXISTS `Answer` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `topic` text DEFAULT null
);

CREATE TABLE IF NOT EXISTS `MadeUp` (
  `questionid` int,
  `answerid` int,
  `correct` boolean,
  PRIMARY KEY(`questionid`, `answerid`)
);

ALTER TABLE `Release` ADD FOREIGN KEY (`email`) REFERENCES `Contributor` (`email`);
ALTER TABLE `Release` ADD FOREIGN KEY (`id`) REFERENCES `Video` (`id`);
ALTER TABLE `Composition` ADD FOREIGN KEY (`videoid`) REFERENCES `Video` (`id`);
ALTER TABLE `Composition` ADD FOREIGN KEY (`courseid`) REFERENCES `Course` (`id`);
ALTER TABLE `Enrollment` ADD FOREIGN KEY (`email`) REFERENCES `Student` (`email`);
ALTER TABLE `Enrollment` ADD FOREIGN KEY (`id`) REFERENCES `Course` (`id`);
ALTER TABLE `Visualization` ADD FOREIGN KEY (`email`) REFERENCES `Student` (`email`);
ALTER TABLE `Visualization` ADD FOREIGN KEY (`id`) REFERENCES `Video` (`id`);
ALTER TABLE `Test` ADD FOREIGN KEY (`courseid`) REFERENCES `Course` (`id`);
ALTER TABLE `Test` ADD FOREIGN KEY (`question`) REFERENCES `Question` (`id`);
ALTER TABLE `MadeUp` ADD FOREIGN KEY (`questionid`) REFERENCES `Question` (`id`);
ALTER TABLE `MadeUp` ADD FOREIGN KEY (`answerid`) REFERENCES `Answer` (`id`);