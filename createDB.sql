CREATE DATABASE `flaskylearn`;
USE `flaskylearn`;

CREATE TABLE `Contributor` (
  `email` varchar(255) PRIMARY KEY,
  `name` varchar(255) DEFAULT null,
  `surname` varchar(255) DEFAULT null,
  `password` varchar(255) DEFAULT null
);

CREATE TABLE `Video` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `description` text DEFAULT null,
  `path` varchar(255) DEFAULT null
);

CREATE TABLE `Course` (
  `id` int PRIMARY KEY,
  `name` varchar(255) DEFAULT null,
  `time` datetime DEFAULT null
);

CREATE TABLE `Student` (
  `email` varchar(255) PRIMARY KEY,
  `name` varchar(255) DEFAULT null,
  `surname` varchar(255) DEFAULT null,
  `password` varchar(255) DEFAULT null
);

CREATE TABLE `Release` (
  `email` varchar(255),
  `id` int,
  PRIMARY KEY (`email`, `id`)
);

CREATE TABLE `Composition` (
  `videoid` int,
  `courseid` int,
  `lesson` int DEFAULT null,
  PRIMARY KEY (`videoid`, `courseid`)
);

CREATE TABLE `Enrollment` (
  `email` varchar(255),
  `id` int,
  `timestamp` datetime DEFAULT null,
  PRIMARY KEY (`email`, `id`)
);

CREATE TABLE `Visualization` (
  `email` varchar(255),
  `id` int,
  `timestamp` datetime,
  PRIMARY KEY (`email`, `id`, `timestamp`)
);

ALTER TABLE `Release` ADD FOREIGN KEY (`email`) REFERENCES `Contributor` (`email`);

ALTER TABLE `Release` ADD FOREIGN KEY (`id`) REFERENCES `Video` (`id`);

ALTER TABLE `Composition` ADD FOREIGN KEY (`videoid`) REFERENCES `Video` (`id`);

ALTER TABLE `Composition` ADD FOREIGN KEY (`courseid`) REFERENCES `Course` (`id`);

ALTER TABLE `Enrollment` ADD FOREIGN KEY (`email`) REFERENCES `Student` (`email`);

ALTER TABLE `Enrollment` ADD FOREIGN KEY (`id`) REFERENCES `Course` (`id`);

ALTER TABLE `Visualization` ADD FOREIGN KEY (`email`) REFERENCES `Student` (`email`);

ALTER TABLE `Visualization` ADD FOREIGN KEY (`id`) REFERENCES `Video` (`id`);

