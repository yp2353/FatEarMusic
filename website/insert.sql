-- Password is the same as username. Here it is stored as hashed
INSERT INTO `user`(`username`, `pwd`, `fname`, `lname`, `lastlogin`, `nickname`) VALUES ('yp2353','sha256$NCl5Kn62Ul4U0qW1$b7c241e66ae07cd570b54ee2b69c4c5ef22221404c9d16fa44ad6cb62df033c6','Alicia','Pan','2023-05-07 21:41:03','yp');
INSERT INTO `user`(`username`, `pwd`, `fname`, `lname`, `lastlogin`, `nickname`) VALUES ('kk123','sha256$rMfwmEvWY8LBcYk5$9e5889db17b55a0d57c96b2a1043062b7f4b396de4a3895615ba163025fefb3f','Kim','Berley','2023-05-07 14:42:11','kimmy');
INSERT INTO `user`(`username`, `pwd`, `fname`, `lname`, `lastlogin`, `nickname`) VALUES ('phy123','sha256$yOsLwpe03r2NAywQ$7c071d316bad8e6830159e1c07afe377b4d8c699a18871ff21efd769cb31c823','Phyllis','Frankl','2023-05-06 10:19:11','prof');


INSERT INTO `song` (`songID`, `title`, `releaseDate`, `songURL`) VALUES ('1', 'Sugar', '2019-08-12 02:10:03', 'https://www.youtube.com/watch?v=09R8_2nJtjg');
INSERT INTO `song` (`songID`, `title`, `releaseDate`, `songURL`) VALUES ('2', 'Believer', '2018-03-12 12:41:03', 'https://www.youtube.com/watch?v=oppaw2J32ow');
INSERT INTO `song` (`songID`, `title`, `releaseDate`, `songURL`) VALUES ('3', 'SINS', '2022-09-14 21:44:03', 'https://www.youtube.com/watch?v=hvNbMrUNtuc');
INSERT INTO `song` (`songID`, `title`, `releaseDate`, `songURL`) VALUES ('4', 'Peaches', '2021-09-14 09:13:03', 'https://www.youtube.com/watch?v=BydBU2pCkU8');
INSERT INTO `song` (`songID`, `title`, `releaseDate`, `songURL`) VALUES ('5', 'Sugar', '2023-01-29 01:45:17', 'https://youtu.be/5vBGOrI6yBk');
INSERT INTO `song` (`songID`, `title`, `releaseDate`, `songURL`) VALUES ('6', 'Thunder', '2024-03-12 21:41:03', 'https://youtu.be/fKopy74weus');
INSERT INTO `song` (`songID`, `title`, `releaseDate`, `songURL`) VALUES ('7', 'Sugar', '2021-05-07 08:00:03', 'https://youtu.be/HHERRvuG-qs');


INSERT INTO `artist` (`artistID`, `fname`, `lname`, `artistBio`, `artistURL`) VALUES ('1', 'Red', 'Leather', 'A mysterious music artist shrouded in mystery', 'https://pianity.com/red-leather');
INSERT INTO `artist` (`artistID`, `fname`, `lname`, `artistBio`, `artistURL`) VALUES ('2', 'Imagine', 'Dragons', 'American pop rock band based in Las Vegas, Nevada', 'https://www.imaginedragonsmusic.com/#/');
INSERT INTO `artist` (`artistID`, `fname`, `lname`, `artistBio`, `artistURL`) VALUES ('3', 'System', 'of a Down', 'American heavy metal band formed in Glendale, California', 'https://www.systemofadown.com');
INSERT INTO `artist` (`artistID`, `fname`, `lname`, `artistBio`, `artistURL`) VALUES ('4', 'Justin', 'Bieber', 'Canadian singer', 'https://www.justinbiebermusic.com/');
INSERT INTO `artist` (`artistID`, `fname`, `lname`, `artistBio`, `artistURL`) VALUES ('5', 'Maroon', '5', 'Lead vocalist Adam Levine..', 'https://www.maroon5.com/');
INSERT INTO `artist` (`artistID`, `fname`, `lname`, `artistBio`, `artistURL`) VALUES ('6', 'Zubi', 'Soul', 'Management ade@chakratek.co.uk', 'https://www.instagram.com/zubisoul/');
INSERT INTO `artist` (`artistID`, `fname`, `lname`, `artistBio`, `artistURL`) VALUES ('7', 'Daniel', 'Caesar', 'R&B', 'https://danielcaesar.com');


INSERT INTO `artistPerformsSong` (`artistID`, `songID`) VALUES ('1', '3');
INSERT INTO `artistPerformsSong` (`artistID`, `songID`) VALUES ('2', '6');
INSERT INTO `artistPerformsSong` (`artistID`, `songID`) VALUES ('6', '7');
INSERT INTO `artistPerformsSong` (`artistID`, `songID`) VALUES ('4', '4');
INSERT INTO `artistPerformsSong` (`artistID`, `songID`) VALUES ('7', '4');
INSERT INTO `artistPerformsSong` (`artistID`, `songID`) VALUES ('2', '2');
INSERT INTO `artistPerformsSong` (`artistID`, `songID`) VALUES ('5', '1');
INSERT INTO `artistPerformsSong` (`artistID`, `songID`) VALUES ('3', '5');


INSERT INTO `album` (`albumID`) VALUES ('SINS');
INSERT INTO `album` (`albumID`) VALUES ('Evo');
INSERT INTO `album` (`albumID`) VALUES ('Just');
INSERT INTO `album` (`albumID`) VALUES ('V');
INSERT INTO `album` (`albumID`) VALUES ('Down');


INSERT INTO `songInAlbum` (`albumID`, `songID`) VALUES ('SINS', '3');
INSERT INTO `songInAlbum` (`albumID`, `songID`) VALUES ('Evo', '6');
INSERT INTO `songInAlbum` (`albumID`, `songID`) VALUES ('Just', '4');
INSERT INTO `songInAlbum` (`albumID`, `songID`) VALUES ('Evo', '2');
INSERT INTO `songInAlbum` (`albumID`, `songID`) VALUES ('V', '1');
INSERT INTO `songInAlbum` (`albumID`, `songID`) VALUES ('Down', '5');


INSERT INTO `follows` (`follower`, `follows`, `createdAt`) VALUES ('yp2353', 'kk123', '2022-09-01 09:42:40');
INSERT INTO `follows` (`follower`, `follows`, `createdAt`) VALUES ('yp2353', 'phy123', '2023-05-07 14:42:11');


INSERT INTO `friend` (`user1`, `user2`, `acceptStatus`, `requestSentBy`, `createdAt`, `updatedAt`) VALUES ('kk123', 'yp2353', 'Accepted', 'yp2353', '2022-09-01 09:44:42', '2022-09-10 05:44:42');
INSERT INTO `friend` (`user1`, `user2`, `acceptStatus`, `requestSentBy`, `createdAt`, `updatedAt`) VALUES ('phy123', 'yp2353', 'Pending', 'yp2353', '2023-03-13 09:45:53', NULL);


INSERT INTO `rateAlbum`(`username`, `albumID`, `stars`, `ratingDate`) VALUES ('yp2353','SINS','5','2023-05-07 20:42:11');


INSERT INTO `rateSong` (`username`, `songID`, `stars`, `ratingDate`) VALUES ('yp2353', '1', '5', '2023-03-13 09:42:40');
INSERT INTO `rateSong` (`username`, `songID`, `stars`, `ratingDate`) VALUES ('yp2353', '4', '2', '2022-11-06 09:44:42');
INSERT INTO `rateSong` (`username`, `songID`, `stars`, `ratingDate`) VALUES ('kk123', '2', '1', '2023-01-16 09:45:53');
INSERT INTO `rateSong` (`username`, `songID`, `stars`, `ratingDate`) VALUES ('kk123', '1', '3', '2023-01-16 09:44:53');
INSERT INTO `rateSong` (`username`, `songID`, `stars`, `ratingDate`) VALUES ('phy123', '3', '3', '2022-11-21 14:42:11');


INSERT INTO `reviewAlbum` (`username`, `albumID`, `reviewText`, `reviewDate`) VALUES ('yp2353', 'Evo', 'Good', '2023-01-16 09:44:53');


INSERT INTO `reviewSong` (`username`, `songID`, `reviewText`, `reviewDate`) VALUES ('yp2353', '1', 'I love it', '2023-02-16 09:44:53');
INSERT INTO `reviewSong` (`username`, `songID`, `reviewText`, `reviewDate`) VALUES ('kk123', '4', 'A good song to listen to on a road trip', '2023-08-16 10:44:53');
INSERT INTO `reviewSong` (`username`, `songID`, `reviewText`, `reviewDate`) VALUES ('yp2353', '4', 'Relaxing!', '2023-02-16 09:44:53');


INSERT INTO `songGenre` (`songID`, `genre`) VALUES ('1', 'pop');
INSERT INTO `songGenre` (`songID`, `genre`) VALUES ('2', 'pop');
INSERT INTO `songGenre` (`songID`, `genre`) VALUES ('3', 'rock');
INSERT INTO `songGenre` (`songID`, `genre`) VALUES ('4', 'pop');
INSERT INTO `songGenre` (`songID`, `genre`) VALUES ('5', 'rap');
INSERT INTO `songGenre` (`songID`, `genre`) VALUES ('6', 'pop');
INSERT INTO `songGenre` (`songID`, `genre`) VALUES ('7', 'metal');


INSERT INTO `userFanOfArtist` (`username`, `artistID`) VALUES ('yp2353', '2');


INSERT INTO `playlist` (`listID`, `listName`, `createdAt`, `createdBy`, `playlistDescription`) VALUES ('0', 'Pop Songs', '2023-02-12 09:44:11', 'yp2353', 'All the pop songs I like');
INSERT INTO `playlist` (`listID`, `listName`, `createdAt`, `createdBy`) VALUES ('1', 'My Favs', '2023-04-27 16:23:09', 'yp2353');
INSERT INTO `playlist` (`listID`, `listName`, `createdAt`, `createdBy`, `playlistDescription`) VALUES ('2', 'My Favs', '2023-05-27 16:23:09', 'kk123', 'Best songs!');

INSERT INTO `songInPlaylist` (`listID`, `songID`) VALUES ('0', '1');

