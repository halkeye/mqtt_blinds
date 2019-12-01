TAG := `/bin/date "+%Y%m%d"`

build:
	docker build -t halkeye/mqtt_blinds:$(TAG) .
push:
	docker push halkeye/mqtt_blinds:$(TAG)
