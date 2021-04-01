CREATE DATABASE IF NOT EXISTS `iotCli` ;
USE `iotCli`;
CREATE TABLE IF NOT EXISTS `serviceContainers` ( `containerId` int NOT NULL AUTO_INCREMENT, `containerName` varchar(255) NOT NULL DEFAULT 'AWS_Container', `containerIp` varchar(16) DEFAULT '0.0.0.0', `status` enum('active','inactive') NOT NULL DEFAULT 'active', `description` varchar(255) DEFAULT NULL, `createdAt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP, `updatedAt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, PRIMARY KEY (`containerId`)) ENGINE=InnoDB DEFAULT CHARSET=latin1;
INSERT INTO `serviceContainers` (`containerId`, `containerName`, `containerIp`, `status`, `description`, `createdAt`, `updatedAt`) VALUES (1, 'TestContainer', '0.0.0.0', 'active', 'Default Container', '2020-02-13 17:04:45', '2020-02-14 16:13:33');
CREATE TABLE IF NOT EXISTS `awsCredentials` ( `accountId` int NOT NULL AUTO_INCREMENT, `accountName` varchar(200) NOT NULL DEFAULT 'AWS_Account', `regionAWS` varchar(50) NOT NULL, `accessKey` varchar(255) NOT NULL, `secretKey` varchar(255) NOT NULL, `status` enum('active','inactive') NOT NULL DEFAULT 'active', `containerId` int DEFAULT '1', `description` varchar(255) DEFAULT NULL, `createdAt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP, `updatedAt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, PRIMARY KEY (`accountId`)) ENGINE=InnoDB DEFAULT CHARSET=latin1;
CREATE TABLE IF NOT EXISTS `serviceRequest` ( `jobId` int NOT NULL AUTO_INCREMENT, `uid` varchar(60) DEFAULT NULL, `task` varchar(60) NOT NULL, `operation` varchar(60) NOT NULL, `attrData` varchar(5000) DEFAULT NULL, `awsAccountId` int NOT NULL, `scheduledAt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP, `processedAt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP, `processStatus` enum('success','fail','retry','queued') DEFAULT 'queued', `retryCount` int NOT NULL DEFAULT '0', `processingTime` int NOT NULL DEFAULT '0', `response` varchar(500) DEFAULT NULL, `active` enum('Y','N') NOT NULL DEFAULT 'Y', `createdAt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, `updatedAt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, PRIMARY KEY (`jobId`)) ENGINE=InnoDB DEFAULT CHARSET=latin1;
CREATE TABLE IF NOT EXISTS `thingGroup` ( `thingGroupId` int NOT NULL AUTO_INCREMENT, `thingGroupName` varchar(255) NOT NULL, `thingGroupDescription` varchar(4096) DEFAULT NULL, `parentGroupId` int DEFAULT NULL, `status` enum('active','inactive') DEFAULT 'inactive', `thingGroupUID` varchar(255) DEFAULT NULL, `tags` varchar(255) DEFAULT NULL, `thingGroupArn` varchar(255) DEFAULT NULL, `version` int NOT NULL DEFAULT '1', `awsAccountId` int NOT NULL, `additionalData` varchar(1024) DEFAULT NULL, `createdAt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP, `updatedAt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, PRIMARY KEY (`thingGroupId`), KEY `FK_thingGroup_awsCredentials` (`awsAccountId`), CONSTRAINT `FK_thingGroup_awsCredentials` FOREIGN KEY (`awsAccountId`) REFERENCES `awsCredentials` (`accountId`)) ENGINE=InnoDB DEFAULT CHARSET=latin1;
CREATE TABLE IF NOT EXISTS `things` ( `thingId` int NOT NULL AUTO_INCREMENT, `thingName` varchar(255) NOT NULL, `version` int DEFAULT '1', `thingArn` varchar(255) DEFAULT NULL, `thingDescription` varchar(4096) DEFAULT NULL, `thingTypeId` int DEFAULT NULL, `thingUID` varchar(50) DEFAULT NULL, `awsAccountId` int NOT NULL, `thingGroupId` int DEFAULT NULL, `createdAt` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP, `lastUpdated` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, `status` enum('active','inactive') NOT NULL DEFAULT 'inactive', PRIMARY KEY (`thingId`), KEY `FK_things_awsCredentials` (`awsAccountId`), CONSTRAINT `FK_things_awsCredentials` FOREIGN KEY (`awsAccountId`) REFERENCES `awsCredentials` (`accountId`)) ENGINE=InnoDB DEFAULT CHARSET=latin1;
CREATE TABLE IF NOT EXISTS `thingType` ( `thingTypeId` int NOT NULL AUTO_INCREMENT, `thingTypeName` varchar(255) NOT NULL DEFAULT 'Thing', `thingTypeDescription` varchar(4096) DEFAULT NULL, `thingTypeArn` varchar(255) DEFAULT NULL, `thingTypeUID` varchar(1024) DEFAULT NULL, `awsAccountId` int NOT NULL, `additionalData` varchar(2048) DEFAULT NULL, `status` enum('active','inactive','deprecated') NOT NULL DEFAULT 'active', `dateAdded` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, `dateUpdated` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, PRIMARY KEY (`thingTypeId`), KEY `FK_thingType_awsCredentials` (`awsAccountId`), CONSTRAINT `FK_thingType_awsCredentials` FOREIGN KEY (`awsAccountId`) REFERENCES `awsCredentials` (`accountId`)) ENGINE=InnoDB DEFAULT CHARSET=latin1;


#End for all the sql should be ENGINE=InnoDB DEFAULT CHARSET=latin1;