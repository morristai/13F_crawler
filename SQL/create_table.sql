create table point_72."2020-03-31"
(
	"Security" TEXT,
	"Ticker" TEXT,
	"Shares" INT,
	"Value (x$1000)" INT,
	"Activity(%)" NUMERIC,
	"Port(%)" NUMERIC
);

create index "2020-03-31_ticker_index"
	on point_72."2020-03-31" ("Ticker");

