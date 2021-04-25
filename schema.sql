DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS article;
DROP TABLE IF EXISTS book;
DROP TABLE IF EXISTS log;
DROP TABLE IF EXISTS post;
DROP TABLE IF EXISTS reply;
DROP TABLE IF EXISTS video;
DROP TABLE IF EXISTS follow;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  isadmin INTEGER DEFAULT 0 CHECK(isadmin BETWEEN 0 AND 1) NOT NULL
);

CREATE TABLE article (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  topic TEXT NOT NULL,
  body TEXT NOT NULL,
  image TEXT,
  turn INTEGER NOT NULL,

  button TEXT,
  link TEXT,

  FOREIGN KEY (title) REFERENCES book (title)
);

CREATE TABLE book (
  title TEXT PRIMARY KEY NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  author_id INTEGER NOT NULL,

  FOREIGN KEY (author_id) REFERENCES user (id)
);

CREATE TABLE log (
  user_id INTEGER NULL,
  tag TEXT NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES user (id)
);

CREATE TABLE post (
  user_id INTEGER NOT NULL,
  id INTEGER PRIMARY KEY AUTOINCREMENT, 
  topic TEXT NOT NULL,
  body TEXT NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

  FOREIGN KEY (user_id) REFERENCES user (id)
);

CREATE TABLE reply (
  id INTEGER PRIMARY KEY AUTOINCREMENT, 
  user_id INTEGER NOT NULL,
  post_id INTEGER NOT NULL, 

  body TEXT NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

  FOREIGN KEY (user_id) REFERENCES user (id),
  FOREIGN KEY (post_id) REFERENCES post (id)
);

CREATE TABLE video (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  topic TEXT NOT NULL,
  body TEXT NOT NULL,
  link TEXT NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE follow (
  follower_id INTEGER NOT NULL,
  followed_id INTEGER NOT NULL,

  PRIMARY KEY (follower_id,followed_id),

  FOREIGN KEY (follower_id) REFERENCES user (id),
  FOREIGN KEY (followed_id) REFERENCES user (id)
);

INSERT INTO user (id,username,password,isadmin) VALUES (1,"admin","pbkdf2:sha256:150000$fhkhNWLP$150986775cdd740ed80915461a0aa0afb150d17ad0c50bcb4ad13e97cbc3af28",1);

INSERT INTO book (title,author_id) VALUES 
(
  "home",
  1
);

INSERT INTO article (id,title,topic,body,turn) VALUES 
(
  1,
  "home",
  "Modern, scalable web apps with .NET and C#",
  "Use .NET and C# to create websites based on HTML5, CSS, and JavaScript that are secure, fast, and can scale to millions of users.",
  0
);

INSERT INTO article (id,title,topic,body,turn) VALUES 
(
  2,
  "home",
  "Interactive web UI with C#",
  "Blazor is a feature of ASP.NET for building interactive web UIs using C# instead of JavaScript. Blazor gives you real .NET running in the browser on WebAssembly.",
  1
);

INSERT INTO article (id,title,topic,body,turn) VALUES 
(
  3,
  "home",
  "Dynamically render HTML with Razor",
  "With Razor you can use any HTML or C# feature. You get great editor support for both, including IntelliSense, which provides auto-completion, real-time type and syntax checking, and more.",
  2
);

