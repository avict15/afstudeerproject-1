BEGIN TRANSACTION;
CREATE TABLE [chargingpoint] (
	[id]	INTEGER NOT NULL,
	[price]	INTEGER,
	[availability]	INTEGER,
	PRIMARY KEY([id])
);
INSERT INTO [chargingpoint] VALUES (1, 1,0);
INSERT INTO [chargingpoint] VALUES (2,2,0);
INSERT INTO [chargingpoint] VALUES (3,3,0);
INSERT INTO [chargingpoint] VALUES (4,4,0);
CREATE TABLE [user] (
	[id]	INTEGER NOT NULL IDENTITY(1, 1),
	[name]	VARCHAR ( 64 ),
	[username]	VARCHAR ( 64 ),
	[email]	VARCHAR ( 120 ),
	[password_hash]	VARCHAR ( 128 ),
	[licenseplate]	VARCHAR ( 15 ) UNIQUE,
	[last_message_read_time] datetime,
	PRIMARY KEY([id])
);
CREATE TABLE [session] (
	[id]	INTEGER NOT NULL IDENTITY(1, 1),
	[created]	datetime,
	[endtime]	datetime,
	[user_id]	INTEGER,
	[chargingpoint_id]	INTEGER,
	FOREIGN KEY([chargingpoint_id]) REFERENCES [chargingpoint]([id]),
	PRIMARY KEY([id]),
	FOREIGN KEY([user_id]) REFERENCES [user]([id])
);

CREATE TABLE [message] (
	[id]	INTEGER NOT NULL IDENTITY(1, 1),
	[recipient_id]	INTEGER,
	[body]	VARCHAR ( 140 ),
	[timestamp]	datetime,
	[chargingpoint_id]	INTEGER,
	[session_id]	INTEGER,
	FOREIGN KEY([chargingpoint_id]) REFERENCES [chargingpoint]([id]),
	PRIMARY KEY([id]),
	FOREIGN KEY([recipient_id]) REFERENCES [user]([id]),
	FOREIGN KEY([session_id]) REFERENCES [session]([id])
);


COMMIT;