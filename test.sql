CREATE TABLE [AspNetRoles] (
    [Id] nvarchar(450) NOT NULL,
    [Name] nvarchar(256) NULL,
    [NormalizedName] nvarchar(256) NULL,
    [ConcurrencyStamp] nvarchar(max) NULL,
    CONSTRAINT [PK_AspNetRoles] PRIMARY KEY ([Id])
);
GO

CREATE TABLE [AspNetUsers] (
    [Id] nvarchar(450) NOT NULL,
    [UserDataId] int NOT NULL,
    [UserName] nvarchar(256) NULL,
    [NormalizedUserName] nvarchar(256) NULL,
    [Email] nvarchar(256) NULL,
    [NormalizedEmail] nvarchar(256) NULL,
    [EmailConfirmed] bit NOT NULL,
    [PasswordHash] nvarchar(max) NULL,
    [SecurityStamp] nvarchar(max) NULL,
    [ConcurrencyStamp] nvarchar(max) NULL,
    [PhoneNumber] nvarchar(max) NULL,
    [PhoneNumberConfirmed] bit NOT NULL,
    [TwoFactorEnabled] bit NOT NULL,
    [LockoutEnd] datetimeoffset NULL,
    [LockoutEnabled] bit NOT NULL,
    [AccessFailedCount] int NOT NULL,
    CONSTRAINT [PK_AspNetUsers] PRIMARY KEY ([Id])
);
GO

CREATE TABLE [Files] (
    [Id] int NOT NULL IDENTITY,
    [FileName] nvarchar(255) NULL,
    [ContentType] nvarchar(100) NOT NULL,
    [Size] bigint NOT NULL,
    [FileData] varbinary(max) NOT NULL,
    [UploadDate] datetime2 NOT NULL,
    CONSTRAINT [PK_Files] PRIMARY KEY ([Id])
);
GO

CREATE TABLE [AspNetRoleClaims] (
    [Id] int NOT NULL IDENTITY,
    [RoleId] nvarchar(450) NOT NULL,
    [ClaimType] nvarchar(max) NULL,
    [ClaimValue] nvarchar(max) NULL,
    CONSTRAINT [PK_AspNetRoleClaims] PRIMARY KEY ([Id]),
    CONSTRAINT [FK_AspNetRoleClaims_AspNetRoles_RoleId] FOREIGN KEY ([RoleId]) REFERENCES [AspNetRoles] ([Id]) ON DELETE CASCADE
);
GO

CREATE TABLE [AspNetUserClaims] (
    [Id] int NOT NULL IDENTITY,
    [UserId] nvarchar(450) NOT NULL,
    [ClaimType] nvarchar(max) NULL,
    [ClaimValue] nvarchar(max) NULL,
    CONSTRAINT [PK_AspNetUserClaims] PRIMARY KEY ([Id]),
    CONSTRAINT [FK_AspNetUserClaims_AspNetUsers_UserId] FOREIGN KEY ([UserId]) REFERENCES [AspNetUsers] ([Id]) ON DELETE CASCADE
);
GO

CREATE TABLE [AspNetUserLogins] (
    [LoginProvider] nvarchar(450) NOT NULL,
    [ProviderKey] nvarchar(450) NOT NULL,
    [ProviderDisplayName] nvarchar(max) NULL,
    [UserId] nvarchar(450) NOT NULL,
    CONSTRAINT [PK_AspNetUserLogins] PRIMARY KEY ([LoginProvider], [ProviderKey]),
    CONSTRAINT [FK_AspNetUserLogins_AspNetUsers_UserId] FOREIGN KEY ([UserId]) REFERENCES [AspNetUsers] ([Id]) ON DELETE CASCADE
);
GO

CREATE TABLE [AspNetUserRoles] (
    [UserId] nvarchar(450) NOT NULL,
    [RoleId] nvarchar(450) NOT NULL,
    CONSTRAINT [PK_AspNetUserRoles] PRIMARY KEY ([UserId], [RoleId]),
    CONSTRAINT [FK_AspNetUserRoles_AspNetRoles_RoleId] FOREIGN KEY ([RoleId]) REFERENCES [AspNetRoles] ([Id]) ON DELETE CASCADE,
    CONSTRAINT [FK_AspNetUserRoles_AspNetUsers_UserId] FOREIGN KEY ([UserId]) REFERENCES [AspNetUsers] ([Id]) ON DELETE CASCADE
);
GO

CREATE TABLE [AspNetUserTokens] (
    [UserId] nvarchar(450) NOT NULL,
    [LoginProvider] nvarchar(450) NOT NULL,
    [Name] nvarchar(450) NOT NULL,
    [Value] nvarchar(max) NULL,
    CONSTRAINT [PK_AspNetUserTokens] PRIMARY KEY ([UserId], [LoginProvider], [Name]),
    CONSTRAINT [FK_AspNetUserTokens_AspNetUsers_UserId] FOREIGN KEY ([UserId]) REFERENCES [AspNetUsers] ([Id]) ON DELETE CASCADE
);
GO

CREATE TABLE [UserData] (
    [Id] int NOT NULL IDENTITY,
    [Bio] nvarchar(max) NULL,
    [UserId] nvarchar(450) NOT NULL,
    [PictureId] int NULL,
    [CoverId] int NULL,
    CONSTRAINT [PK_UserData] PRIMARY KEY ([Id]),
    CONSTRAINT [FK_UserData_AspNetUsers_UserId] FOREIGN KEY ([UserId]) REFERENCES [AspNetUsers] ([Id]) ON DELETE CASCADE,
    CONSTRAINT [FK_UserData_Files_CoverId] FOREIGN KEY ([CoverId]) REFERENCES [Files] ([Id]),
    CONSTRAINT [FK_UserData_Files_PictureId] FOREIGN KEY ([PictureId]) REFERENCES [Files] ([Id])
);
GO

CREATE TABLE [Posts] (
    [Id] int NOT NULL IDENTITY,
    [Title] nvarchar(max) NOT NULL,
    [Content] nvarchar(max) NULL,
    [Date] datetime2 NOT NULL,
    [PosterId] nvarchar(450) NOT NULL,
    [ParentPostId] int NULL,
    [AttachmentId] int NULL,
    [UserDataId] int NULL,
    CONSTRAINT [PK_Posts] PRIMARY KEY ([Id]),
    CONSTRAINT [FK_Posts_AspNetUsers_PosterId] FOREIGN KEY ([PosterId]) REFERENCES [AspNetUsers] ([Id]) ON DELETE NO ACTION,
    CONSTRAINT [FK_Posts_Files_AttachmentId] FOREIGN KEY ([AttachmentId]) REFERENCES [Files] ([Id]),
    CONSTRAINT [FK_Posts_Posts_ParentPostId] FOREIGN KEY ([ParentPostId]) REFERENCES [Posts] ([Id]),
    CONSTRAINT [FK_Posts_UserData_UserDataId] FOREIGN KEY ([UserDataId]) REFERENCES [UserData] ([Id])
);
GO

CREATE TABLE [PostDislikers] (
    [DislikedPostsId] int NOT NULL,
    [DislikersId] nvarchar(450) NOT NULL,
    CONSTRAINT [PK_PostDislikers] PRIMARY KEY ([DislikedPostsId], [DislikersId]),
    CONSTRAINT [FK_PostDislikers_AspNetUsers_DislikersId] FOREIGN KEY ([DislikersId]) REFERENCES [AspNetUsers] ([Id]) ON DELETE CASCADE,
    CONSTRAINT [FK_PostDislikers_Posts_DislikedPostsId] FOREIGN KEY ([DislikedPostsId]) REFERENCES [Posts] ([Id]) ON DELETE CASCADE
);
GO

CREATE TABLE [PostLikers] (
    [LikedPostsId] int NOT NULL,
    [LikersId] nvarchar(450) NOT NULL,
    CONSTRAINT [PK_PostLikers] PRIMARY KEY ([LikedPostsId], [LikersId]),
    CONSTRAINT [FK_PostLikers_AspNetUsers_LikersId] FOREIGN KEY ([LikersId]) REFERENCES [AspNetUsers] ([Id]) ON DELETE CASCADE,
    CONSTRAINT [FK_PostLikers_Posts_LikedPostsId] FOREIGN KEY ([LikedPostsId]) REFERENCES [Posts] ([Id]) ON DELETE CASCADE
);
GO