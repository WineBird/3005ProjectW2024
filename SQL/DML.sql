Insert into Member(Name, mUname, Password, Height, Weight)
Values
('Dell', 'Engineer', '$2b$12$q5wZGE5M.5MKlUTVZt.A7.8WWYAglixxZcjfkgUS7PLNZZwPOG1oW', 155, 65),
('Tavish', 'TheDemoman', '$2b$12$aH9kj7/RDzLwor4.T7NzEuDSmEFfLi2TTwAITWeuk3KDm9WZ.z1Dy', 180, 80),
('Misha', 'hwg', '$2b$12$euWOaRp2tK/UJoEQnhAma.D5GIevH/pATwO0k9kCSoIHF4wk4ix7u', 200, 115),
('Jeremy', '985', '$2b$12$JlX4lsQr1TflWUMn3F.AFuSPdFMdITbyUEGYyndjz0ikdOCqHHoJG', 167, 56),
('Deimos', 'Deimos', '$2b$12$w7.WHlfc.lt1Ivxoz3f0R.b3FNELBxOGAV.FQFlosLPUwLZY129cq', 150, 55);

Insert into Trainer(Name, tUname, Password)
Values
('Hale', 'MannCo', '$2b$12$KI51uRvzj0E23L2gwxVrI.mLl5PEox18pklKUCsMFO.qWbiMA1tC6'),
('Steve', 'Minecraft', '$2b$12$Yciww1HXt.h5Ozwg6hjm2u.tIbnJA8k8doJZjnprHnALED9jR4Oum'),
('Hank', 'TheProtagonist', '$2b$12$TU9pGm6vt3Mx2u8BfGMt0Oy3M9Rg4qz/evtzm8/NIeRtSbDFL8NA.');

Insert into Administrator(Name, aUname, Password)
Values
('Helen', 'RealAdmin', '$2b$12$3rrky.99nilst6NHtvaEqORhk1chBSM3Td6HYJkU8Y7QQpQ.L40Ja'),
('Robert', 'TheHouse', '$2b$12$7WRGqVcJINxdlZAQJnAdxOgEk8wZwPwxgEdUq7NaaNInUoYJ0Ldyu'),
('Janitor', '50Blessings', '$2b$12$82BdyjVyRQv/Srmbw/j/M.pNNvUtbOr8ummuPSWZOx31vod63aajy');

Insert into Achievement(mUname, Description, AchDate)
Values
('985', 'jumped twice in 1 jump', '1991-12-28'),
('985', 'jumped 30 times in 1 jump', '2011-12-28'),
('985', 'jumped twice in 1 jump', '1991-12-28'),
('TheDemoman', 'Put my eye back in', '2013-05-15'),
('TheDemoman', 'big eye', '2013-10-31'),
('Deimos', 'I am alive', '2023-11-11');

Insert into Goal(mUname, WeightGoal, TimeGoal)
Values
('985', 16, 589);

Insert into Bill(Amount, IS_PAID, IS_VERIFIED, mUname)
Values
(1000, FALSE ,FALSE, 'Engineer'),
(1001, TRUE, FALSE, 'TheDemoman'),
(1002, TRUE, TRUE, 'hwg'),
(1003, TRUE, TRUE, '985');

Insert into VerifiedBy(bID,aUname)
Values
(2, 'TheHouse'),
(3, '50Blessings');

Insert into Availability(tUname, aDate)
Values
('MannCo', '2024-04-01'),
('MannCo', '2024-04-02'),
('MannCo', '2024-04-03'),
('MannCo', '2024-04-04'),
('Minecraft', '2024-05-01'),
('Minecraft', '2024-05-02'),
('Minecraft', '2024-05-03'),
('Minecraft', '2024-05-04'),
('TheProtagonist', '2024-03-01'),
('TheProtagonist', '2024-03-02'),
('TheProtagonist', '2024-05-01'),
('TheProtagonist', '2024-05-02');

Insert into Room(EquipCond)
Values
(100),
(50),
(50),
(50),
(25),
(0);

Insert into PersonalSession(SessionDate, mUname, tUname, rID)
Values
('2024-04-01', 'Engineer', 'MannCo',5),
('2024-04-02', 'TheDemoman', 'MannCo',5),
('2024-04-03', 'hwg', 'MannCo',5),
('2024-05-01', '985', 'Minecraft',1),
('2024-03-02', 'Deimos', 'TheProtagonist',2),
('2024-05-01', 'Deimos', 'TheProtagonist',2);

Insert into GroupSession(SessionDate, Description, tUname, rID)
Values
('2024-04-04', 'Expired session test', 'MannCo', 3),
('2024-05-04', 'Available session test', 'Minecraft', 3);

Insert into Group_Participant(gSID, mUname)
Values
(1, '985'),
(1, 'hwg'),
(1, 'Deimos'),
(2, 'Engineer');