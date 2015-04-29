PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE "GRADEBOOK" (
	"intCompletionReportID" INTEGER, 
	"intInstitutionID" INTEGER, 
	"strCompletionReport" VARCHAR(120), 
	"intGroupID" INTEGER, 
	"strGroup" VARCHAR(120), 
	"intStageID" INTEGER, 
	"strStage" VARCHAR(120)
);
INSERT INTO "GRADEBOOK" VALUES(27,44,'sst',74,'ssttt',104,'ssttttt');
INSERT INTO "GRADEBOOK" VALUES(134,151,'Basic/Refresher Course - Human Subjects Research',181,'ssssttttt',211,'ssss');
INSERT INTO "GRADEBOOK" VALUES(241,258,'Basic/Refresher Course - Human Subjects Research',288,'s',318,'stt');
CREATE TABLE "MEMBERS" (
	"intMemberID" INTEGER, 
	"strLastII" VARCHAR(120), 
	"strFirstII" VARCHAR(120), 
	"strUsernameII" VARCHAR(120), 
	"strInstUsername" VARCHAR(120), 
	"strInstEmail" VARCHAR(120), 
	"dteAdded" DATE, 
	"dteAffiliated" DATE, 
	"dteLastLogin" DATE, 
	"strCustom1" VARCHAR(120), 
	"strCustom2" VARCHAR(120), 
	"strCustom3" VARCHAR(120), 
	"strCustom4" VARCHAR(120), 
	"strCustom5" VARCHAR(120), 
	"strSSOCustomAttrib1" VARCHAR(120), 
	"strSSOCustomAttrib2" VARCHAR(120), 
	"strEmployeeNum" VARCHAR(120)
);
INSERT INTO "MEMBERS" VALUES(27,'ttttt','ssstttt','sttt','sssstt','sst','2011-02-26','2011-07-09','2011-12-18','ssttt','tt','ssst','s','sssstttttt','ssttttt','tttt','sssttt');
INSERT INTO "MEMBERS" VALUES(300,'sssttttt','stttt','ssssttt','sstt','t','2011-11-13','2011-04-22','2011-09-05','ttt','ssstt','st','ssss','sstttttt','ttttt','ssstttt','sttt');
INSERT INTO "MEMBERS" VALUES(573,'sttttt','sssstttt','ssttt','tt','ssst','2011-08-26','2011-01-09','2011-06-18','sssttt','stt','sssst','ss','tttttt','sssttttt','stttt','ssssttt');
INSERT INTO "MEMBERS" VALUES(846,'ssssttttt','sstttt','ttt','ssstt','st','2011-05-13','2011-10-22','2011-03-05','sttt','sssstt','sst',NULL,'ssstttttt','sttttt','sssstttt','ssttt');
CREATE TABLE "CRS" (
	"CR_InstitutionID" INTEGER, 
	"MemberID" INTEGER, 
	"EmplID" VARCHAR(120), 
	"StudentID" INTEGER, 
	"InstitutionUserName" VARCHAR(120), 
	"FirstName" VARCHAR(120), 
	"LastName" VARCHAR(120), 
	"memberEmail" VARCHAR(120), 
	"AddedMember" DATETIME, 
	"strCompletionReport" VARCHAR(120), 
	"intGroupID" INTEGER, 
	"strGroup" VARCHAR(120), 
	"intStageID" INTEGER, 
	"intStageNumber" INTEGER, 
	"strStage" VARCHAR(120), 
	"intCompletionReportID" INTEGER, 
	"intMemberStageID" INTEGER, 
	"dtePassed" DATETIME, 
	"intScore" INTEGER, 
	"intPassingScore" INTEGER, 
	"dteExpiration" DATETIME
);
INSERT INTO "CRS" VALUES(27,44,'sst',74,'ssttt','tt','ssst','s','2000-12-24 12:34:56.000000','sss',185,'ssstt',215,232,NULL,262,279,'2000-09-15 12:34:56.000000',325,342,'2000-12-22 12:34:56.000000');
INSERT INTO "CRS" VALUES(388,405,'sssttttt',435,'sss','stttttt','ssssttttt','sstttt','2000-01-15 12:34:56.000000','Basic/Refresher Course - Human Subjects Research',546,'sssstttttt',576,593,'stttt',623,640,'2000-10-06 12:34:56.000000',686,703,'2000-01-13 12:34:56.000000');
INSERT INTO "CRS" VALUES(749,766,'sssstt',796,'sssstttt','ssttt','tt','ssst','2000-02-06 12:34:56.000000','Basic/Refresher Course - Human Subjects Research',907,'ttt',937,954,'sst',984,1001,'2000-11-23 12:34:56.000000',1047,1064,'2000-02-04 12:34:56.000000');
INSERT INTO "CRS" VALUES(1110,1127,'tttttt',1157,'t','sss','stttttt','ssssttttt','2000-03-23 12:34:56.000000','sttttt',1268,'s',1298,1315,'sssttttt',1345,1362,'2000-12-14 12:34:56.000000',1408,1425,'2000-03-21 12:34:56.000000');
INSERT INTO "CRS" VALUES(1471,1488,'sttt',1518,'sttttt','sssstttt','ssttt','tt','2000-04-14 12:34:56.000000','Basic/Refresher Course - Human Subjects Research',1629,'sstttt',1659,1676,'sssstt',1706,1723,'2000-01-05 12:34:56.000000',1769,1786,'2000-04-12 12:34:56.000000');
CREATE TABLE "HumanSubjectsFull" (
	"FirstName" VARCHAR(120), 
	"LastName" VARCHAR(120), 
	"Email" VARCHAR(120), 
	"EmployeeID" VARCHAR(120), 
	"DateCompleted" DATETIME, 
	"Username" VARCHAR(120)
);
INSERT INTO "HumanSubjectsFull" VALUES('R','S','RS@example','J1','2011-08-04 00:00:00.000000','rs');
CREATE TABLE "HumanSubjectsRefresher" (
	"FirstName" VARCHAR(120), 
	"LastName" VARCHAR(120), 
	"Email" VARCHAR(120), 
	"EmployeeID" VARCHAR(120), 
	"CompleteDate" DATETIME, 
	"Username" VARCHAR(120)
);
INSERT INTO "HumanSubjectsRefresher" VALUES('R3','S','RS3@example','J1','2013-08-04 00:00:00.000000','rs3');
CREATE TABLE "HumanSubjectsInPerson" (
	"FirstName" VARCHAR(120), 
	"LastName" VARCHAR(120), 
	"Email" VARCHAR(120), 
	"EmployeeID" VARCHAR(120), 
	"CompleteDate" DATETIME, 
	"Username" VARCHAR(120)
);
INSERT INTO "HumanSubjectsInPerson" VALUES('R2','S','RS2@example','J1','2012-08-04 00:00:00.000000','rs2');
COMMIT;


CREATE TABLE redcap_data (
	project_id INTEGER NOT NULL, 
	event_id INTEGER NOT NULL, 
	record VARCHAR(100) NOT NULL, 
	field_name VARCHAR(100) NOT NULL, 
	value TEXT, 
	PRIMARY KEY (project_id, event_id, record, field_name)
);
