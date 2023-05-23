package db

import (
	"log"
	"openreplay/backend/pkg/memory"
	"time"

	"openreplay/backend/internal/config/db"
	"openreplay/backend/internal/db/datasaver"
	"openreplay/backend/internal/service"
	"openreplay/backend/pkg/queue/types"
)

type dbImpl struct {
	cfg      *db.Config
	consumer types.Consumer
	saver    datasaver.Saver
	mm       memory.Manager
}

func New(cfg *db.Config, consumer types.Consumer, saver datasaver.Saver, mm memory.Manager) service.Interface {
	s := &dbImpl{
		cfg:      cfg,
		consumer: consumer,
		saver:    saver,
		mm:       mm,
	}
	go s.run()
	return s
}

func (d *dbImpl) run() {
	commitTick := time.Tick(d.cfg.CommitBatchTimeout)
	for {
		select {
		case <-commitTick:
			d.commit()
		case msg := <-d.consumer.Rebalanced():
			log.Println(msg)
		default:
			if !d.mm.HasFreeMemory() {
				continue
			}
			if err := d.consumer.ConsumeNext(); err != nil {
				log.Fatalf("Error on consumption: %v", err)
			}
		}
	}
}

func (d *dbImpl) commit() {
	d.saver.Commit()
	d.consumer.Commit()
}

func (d *dbImpl) Stop() {
	d.commit()
	if err := d.saver.Close(); err != nil {
		log.Printf("saver.Close error: %s", err)
	}
	d.consumer.Close()
}
