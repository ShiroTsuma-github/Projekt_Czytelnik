BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "Autor" (
	"autor_id"	INTEGER NOT NULL,
	"autor_nazwa"	TEXT NOT NULL,
	PRIMARY KEY("autor_id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "Gatunek" (
	"gatunek_id"	INTEGER NOT NULL,
	"gatunek_nazwa"	TEXT NOT NULL,
	PRIMARY KEY("gatunek_id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "Ksiazka" (
	"ksiazka_id"	INTEGER NOT NULL,
	"ksiazka_tytul"	TEXT NOT NULL,
	"ksiazka_strony"	INTEGER NOT NULL,
	"ksiazka_przeczytane"	NUMERIC NOT NULL,
	"ksiazka_ocena"	NUMERIC,
	"ksiazka_okladka"	TEXT,
	"ksiazka_komentarz"	TEXT,
	PRIMARY KEY("ksiazka_id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "Tag" (
	"tag_id"	INTEGER NOT NULL,
	"tag_nazwa"	TEXT NOT NULL,
	PRIMARY KEY("tag_id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "ksiazka_autor" (
	"ksiazka_id"	INTEGER NOT NULL,
	"autor_id"	INTEGER NOT NULL,
	FOREIGN KEY("ksiazka_id") REFERENCES "Ksiazka"("ksiazka_id"),
	FOREIGN KEY("autor_id") REFERENCES "Autor"("autor_id"),
	PRIMARY KEY("ksiazka_id","autor_id")
);
CREATE TABLE IF NOT EXISTS "ksiazka_gatunek" (
	"ksiazka_id"	INTEGER NOT NULL,
	"gatunek_id"	INTEGER NOT NULL,
	FOREIGN KEY("gatunek_id") REFERENCES "Gatunek"("gatunek_id"),
	FOREIGN KEY("ksiazka_id") REFERENCES "Ksiazka"("ksiazka_id"),
	PRIMARY KEY("ksiazka_id","gatunek_id")
);
CREATE TABLE IF NOT EXISTS "ksiazka_tag" (
	"tag_id"	INTEGER NOT NULL,
	"ksiazka_id"	INTEGER NOT NULL,
	FOREIGN KEY("tag_id") REFERENCES "Tag"("tag_id"),
	FOREIGN KEY("ksiazka_id") REFERENCES "Ksiazka"("ksiazka_id"),
	PRIMARY KEY("tag_id","ksiazka_id")
);
COMMIT;
