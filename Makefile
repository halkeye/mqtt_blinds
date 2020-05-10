TAG := `/bin/date "+%Y%m%d"`

.PHONY: build
build:
	docker build -t halkeye/mqtt_blinds:$(TAG) .

.PHONY: push
push:
	docker push halkeye/mqtt_blinds:$(TAG)
.PHONY: run
run:
	docker run -it --rm --name blinds halkeye/mqtt_blinds:$(TAG)
