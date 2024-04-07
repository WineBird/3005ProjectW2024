-- easy drop tables, uncomment if needed
/*
DROP TABLE IF EXISTS Member CASCADE;
DROP TABLE IF EXISTS Goal CASCADE;
DROP TABLE IF EXISTS Achievement CASCADE;
DROP TABLE IF EXISTS Trainer CASCADE;
DROP TABLE IF EXISTS Availability CASCADE;
DROP TABLE IF EXISTS Administrator CASCADE;
DROP TABLE IF EXISTS Bill CASCADE;
DROP TABLE IF EXISTS VerifiedBy CASCADE;
DROP TABLE IF EXISTS Room CASCADE;
DROP TABLE IF EXISTS GroupSession CASCADE;
DROP TABLE IF EXISTS Group_Participant CASCADE;
DROP TABLE IF EXISTS Member CASCADE;
*/
-- CREATE DATABASE projectdb;



CREATE TABLE Member
	(
	Name	TEXT NOT NULL,
	mUname	TEXT UNIQUE NOT NULL,
	Password	bytea NOT NULL,
	Height	INT	NOT NULL,
	Weight INT NOT NULL,
	PRIMARY KEY (mUname)
	);

create table Goal
	(
	mUname	TEXT UNIQUE NOT NULL,
	WeightGoal INT NOT NULL,
	TimeGoal INT NOT NULL,
	primary key (mUname),
	foreign key (mUname) references Member(mUname) on delete cascade
	);

create table Achievement
	(
	mUname	TEXT NOT NULL,
	Description TEXT  NOT NULL,
	AchDate Date DEFAULT CURRENT_DATE,
	AchID SERIAL,
	primary key (AchID),
	foreign key (mUname) references Member(mUname) on delete cascade
	);

create table Trainer
	(
	Name	TEXT NOT NULL,
	tUname	TEXT UNIQUE NOT NULL,
	Password	bytea NOT NULL,
	primary key (tUname)
	);

create table Availability
	(
	tUname TEXT not null,
	aDate Date NOT NULL,
	primary key (tUname, aDate),
	foreign key (tUname) REFERENCES Trainer(tUname) on delete cascade
	);

create table Administrator
	(
	Name	TEXT NOT NULL,
	aUname	TEXT UNIQUE NOT NULL,
	Password	bytea NOT NULL,
	primary key (aUname)
	);

create table Bill
	(
	bID	SERIAL,
	Amount INT NOT NULL,
	IS_PAID	boolean NOT NULL default FALSE,
	IS_VERIFIED BOOLEAN NOT NULL default FALSE,
	mUname	text not null,
	primary key (bID),
	foreign key (mUname) references Member(mUname) on delete cascade
	);

create table VerifiedBy
	(
	bID INT,
	aUname text NOT NULL,
	primary key(bID, aUname),
	foreign key (aUname) references Administrator(aUname) on delete cascade,
	foreign key (bID) references Bill(bID) on delete cascade
	);

create table Room
	(
	rID SERIAL,
	EquipCond INT NOT NULL,
	primary key (rID)
	);

create table GroupSession
	(
	gSID SERIAL,
	SessionDate Date default CURRENT_DATE,
	Description TEXT NOT NULL,
	tUname TEXT NOT NULL,
	rID INT NOT NULL,
	primary key (gSID),
	foreign key (tUname) references Trainer(tUname) on delete cascade,
	foreign key (rID) references Room(rID) on delete cascade
	);

create table Group_Participant
	(
	gSID INT not null,
	mUname TEXT NOT null,
	primary key (gSID, mUname),
	foreign key (gSID) references GroupSession(gSID) on delete cascade,
	foreign key (mUname) references Member(mUname) on delete cascade
	);

create table PersonalSession
	(
	pSID SERIAL,
	SessionDate Date default CURRENT_DATE,
	mUname TEXT NOT NULL,
	tUname TEXT NOT NULL,
	rID INT NOT NULL,
	primary key(pSID),
	foreign key (mUname) references Member(mUname) on delete cascade,
	foreign key (tUname) references Trainer(tUname) on delete cascade,
	foreign key (rID) references Room(rID) on delete cascade
	);