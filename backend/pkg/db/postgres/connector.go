package postgres

import (
	"context"
	"github.com/jackc/pgx/v4/pgxpool"
	"go.opentelemetry.io/otel/metric/instrument/syncfloat64"
	"log"
	"openreplay/backend/pkg/monitoring"
)

// Conn contains batches, bulks and cache for all sessions
type Conn struct {
	c                 Pool
	batches           *BatchSet
	bulks             *BulkSet
	sqlRequestTime    syncfloat64.Histogram
	sqlRequestCounter syncfloat64.Counter
}

func NewConn(url string, queueLimit, sizeLimit int, metrics *monitoring.Metrics) *Conn {
	if metrics == nil {
		log.Fatalf("metrics is nil")
	}
	c, err := pgxpool.Connect(context.Background(), url)
	if err != nil {
		log.Println(err)
		log.Fatalln("pgxpool.Connect Error")
	}
	sqlRequestTime, err := metrics.RegisterHistogram("sql_request_time")
	if err != nil {
		log.Printf("can't create sqlRequestTime metric: %s", err)
	}
	sqlRequestCounter, err := metrics.RegisterCounter("sql_request_number")
	if err != nil {
		log.Printf("can't create sqlRequestNumber metric: %s", err)
	}
	pool, err := NewPool(c, sqlRequestTime, sqlRequestCounter)
	if err != nil {
		log.Fatalf("can't create new pool wrapper: %s", err)
	}
	conn := &Conn{
		c:                 pool,
		batches:           NewBatchSet(queueLimit, sizeLimit, metrics),
		bulks:             NewBulkSet(pool),
		sqlRequestTime:    sqlRequestTime,
		sqlRequestCounter: sqlRequestCounter,
	}
	return conn
}

func (conn *Conn) Close() error {
	conn.c.Close()
	return nil
}

func (conn *Conn) insertAutocompleteValue(projectID uint32, tp string, value string) {
	if len(value) == 0 {
		return
	}
	if err := conn.bulks.Get("autocompletes").Append(value, tp, projectID); err != nil {
		log.Printf("autocomplete bulk err: %s", err)
	}
}

func (conn *Conn) batchQueue(sessionID uint64, sql string, args ...interface{}) {
	conn.batches.batchQueue(sessionID, sql, args)
}

func (conn *Conn) updateSessionEvents(sessionID uint64, events, pages int) {
	conn.batches.updateSessionEvents(sessionID, events, pages)
}

func (conn *Conn) CommitBatches() {
	conn.bulks.SendBulks()
	conn.batches.CommitBatches(conn.c)
}

func (conn *Conn) updateBatchSize(sessionID uint64, reqSize int) {
	conn.batches.updateBatchSize(sessionID, reqSize, conn.c)
}

// Send only one batch to pg
func (conn *Conn) commitBatch(sessionID uint64) {
	conn.batches.commitBatch(sessionID, conn.c)
}
