create table Users(
  id serial primary key,
  username varchar(20) unique,
  first_name varchar(20),
  last_name varchar(20),
  email varchar(45),
  date_joined date default current_date,
  token varchar(100),
  password varchar(100)
  );

create table Topic(
id serial primary key,
title	varchar(50),
body	text,
number_of_comments int default 0,
number_of_likes int default 0,
creator_id int,
created	date default current_date
);


create table Comment
(
  id serial primary key,
    body text,
    creator_id int references Users,
    created timestamp default (now() at time zone 'Europe/Moscow'),
    topic_id int references Topic
);


create table TopicLike
(
  topic_id int references Topic,
  user_id  int references Users,
  added    timestamp default (now() at time zone 'Europe/Moscow')
);


insert into Users (username, first_name, last_name, email, password)
values ('OzzyIsCool','Ozzy','Osborne','ozzy.o@gmail.com','5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8'),
       ('Jimmy','James','Bay','jamesbay@gmail.com','5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8'),
       ('Teddy','Ed','Sheeran','edward.sheeran@gmail.com','5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8'),
       ('Voldemort','Tom','Riddle','darklord@gmail.com','5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8'),
       ('DragonsMom','Daenerys','Targarien','stormborn@yahoo.com','5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8');