CREATE TABLE part(
  part_id INT PRIMARY KEY NOT NULL,
  part_description TEXT,
  part_revision INT
);

CREATE TABLE machine(
	machine_location text PRIMARY KEY,
   	machine_theme text,
	machine_active int DEFAULT 1
  );

CREATE TABLE tech(
  tech_id INT PRIMARY KEY NOT NULL,
  tech_password TEXT,
  tech_name TEXT
);


CREATE TABLE workorder(
  workorder_id INT PRIMARY KEY NOT NULL,
  workorder_description TEXT,
  machine_id INT,
  part_id INT,
  FOREIGN KEY (machine_id)
  	REFERENCES machine (machine_id),
  FOREIGN KEY (part_id)
  	REFERENCES part (part_id)
);

INSERT INTO tech VALUES (1,'abc123','root');
INSERT INTO tech VALUES (1,'abc123','user')

INSERT INTO machine VALUES ("A15-02", "Golden Bananas",1);
INSERT INTO machine VALUES ("B12-09", "Bees!",0);

INSERT INTO part VALUES (1234, "Bill Validator",0);
INSERT INTO part VALUES (56789, "Win Switch",0);


