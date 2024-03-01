create table user (
    username varchar(10) not null,
    pwd varchar(200) not null,
    fname varchar(20) not null,
    lname varchar(20) not null,
    lastlogin datetime,
    nickname varchar(20) not null,
    primary key (username)
);

create table song (
    songID varchar(5),
    title varchar(20) not null,
    releaseDate datetime,
    songURL varchar(50),
    primary key (songID)
);

create table artist (
    artistID varchar(5),
    fname varchar(20) not null,
    lname varchar(20) not null,
    artistBio varchar(100),
    artistURL varchar(50),
    primary key (artistID)
);

create table album (
    albumID varchar(5),
    primary key (albumID)
);

create table friend (
    user1 varchar(10),
    user2 varchar(10),
    acceptStatus varchar(10) check (acceptStatus in ('Accepted', 'Pending')),
    requestSentBy varchar(10),
    createdAt datetime,
    updatedAt datetime,
    primary key (user1, user2),
    foreign key (user1) references user(username) on delete cascade,
    foreign key (user2) references user(username) on delete cascade
);

create table follows (
    follower varchar(10),
    follows varchar(10),
    createdAt datetime,
    primary key (follower, follows),
    foreign key (follower) references user(username) on delete cascade,
    foreign key (follows) references user(username) on delete cascade
);

create table rateAlbum (
    username varchar(10),
    albumID varchar(5),
    stars int check (stars in (1,2,3,4,5)),
    ratingDate datetime,
    primary key (username, albumID),
    foreign key (username) references user(username) on delete cascade,
    foreign key (albumID) references album(albumID) on delete cascade
);

create table reviewAlbum (
    username varchar(10),
    albumID varchar(5),
    reviewText varchar(100),
    reviewDate datetime,
    primary key (username, albumID),
    foreign key (username) references user(username) on delete cascade,
    foreign key (albumID) references album(albumID) on delete cascade
);

create table rateSong (
    username varchar(10),
    songID varchar(5),
    stars int check (stars in (1,2,3,4,5)),
    ratingDate datetime,
    primary key (username, songID),
    foreign key (username) references user(username) on delete cascade,
    foreign key (songID) references song(songID) on delete cascade
);

create table reviewSong (
    username varchar(10),
    songID varchar(5),
    reviewText varchar(100),
    reviewDate datetime,
    primary key (username, songID),
    foreign key (username) references user(username) on delete cascade,
    foreign key (songID) references song(songID) on delete cascade
);

create table songInAlbum (
    albumID varchar(5),
    songID varchar(5),
    primary key (albumID, songID),
    foreign key (albumID) references album(albumID) on delete cascade,
    foreign key (songID) references song(songID) on delete cascade
);

create table songGenre (
    songID varchar(5),
    genre varchar(10),
    primary key (songID, genre),
    foreign key (songID) references song(songID) on delete cascade
);

create table artistPerformsSong (
    artistID varchar(5),
    songID varchar(5),
    primary key (artistID, songID),
    foreign key (artistID) references artist(artistID) on delete cascade,
    foreign key (songID) references song(songID) on delete cascade
);

create table userFanOfArtist (
    username varchar(10),
    artistID varchar(5),
    primary key (username, artistID),
    foreign key (username) references user(username) on delete cascade,
    foreign key (artistID) references artist(artistID) on delete cascade
);


create table playlist (
    listID INT UNSIGNED not null,
    listName varchar(50) not null,
    createdAt datetime,
    createdBy varchar(10) not null,
    playlistDescription varchar(100),
  	primary key(listID),
    foreign key (createdBy) references user(username) on delete cascade
);

create table songInPlaylist (
    listID INT UNSIGNED not null,
    songID varchar(10) not null,
  	primary key(listID, songID),
    foreign key (listID) references playlist(listID) on delete cascade,
    foreign key (songID) references song(songID) on delete cascade
);