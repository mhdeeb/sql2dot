SELECT () ;

SELECT () ;
     
  CREATE TABLE department (
    [id] INT PRIMARY KEY NOT NULL,
    PersonID int FOREIGN KEY REFERENCES Persons(PersonID) ON DELETE CASCADE
);

SELECT () ;

CREAtE TABLE [employee] (
    [id] INT NOT NULL,
    [dep_id] INT NOT NULL,
    [managed_dep_id] INT NULL,
    PRIMARY KEY ([id], [dep_id]),
    FOREIGN KEY ([dep_id]) REFERENCES [department]([id]),
    FOREIGN KEY ([managed_dep_id]) REFERENCES [department] ([id]),
    CONSTRAINT [PK_AspNetRoleClaims] PRIMARY KEY ([Id]),
    CONSTRAINT [FK_AspNetRoleClaims_AspNetRoles_RoleId] FOREIGN KEY ([RoleId]) REFERENCES [AspNetRoles] ([Id]) ON DELETE CASCADE
);
