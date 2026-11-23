# DASH-IF Conformance v3.1.0, MPD modules only. See UPSTREAM for the pin and
# the deviations from upstream's Dockerfile.
# PHP pinned to 8.4: the untagged image moved to PHP 8.6, which composer.lock
# at v3.1.0 does not accept (nette/schema, nette/utils, laminas-diactoros).
FROM dunglas/frankenphp:1-php8.4
RUN apt-get update && apt-get install -y --no-install-recommends \
      openjdk-21-jre-headless git unzip libxml2-dev libzip-dev \
 && rm -rf /var/lib/apt/lists/*
RUN install-php-extensions pcntl zip xml dom
COPY --from=composer:2 /usr/bin/composer /usr/bin/composer
WORKDIR /app
COPY composer.json composer.lock ./
RUN composer install --no-interaction --no-scripts --no-dev --prefer-dist || \
    composer install --no-interaction --no-scripts --prefer-dist
COPY . /app
# The tool's XSDs import xlink.xsd (and through it xml.xsd) from www.w3.org.
# Pinned by sha256 and resolved through an XML catalog, so a run needs no
# network: with network on, the tool also tries to fetch the example hosts the
# MPDs name and hangs on them.
COPY w3c-catalog.xml /opt/w3c/catalog.xml
RUN curl -fsSL -o /opt/w3c/xlink.xsd https://www.w3.org/XML/2008/06/xlink.xsd \
 && curl -fsSL -o /opt/w3c/xml.xsd https://www.w3.org/2001/xml.xsd \
 && printf '%s  %s\n' \
      c83df86c7fdc16eb9c862b83dfb53fc1b1a4bcafd6e1d1217199e0188b82f24a /opt/w3c/xlink.xsd \
      61960fb3131e38022caad5360e2f33a3382578ab3c80cd58bd74320ede61b20c /opt/w3c/xml.xsd \
    | sha256sum -c -
ENV XML_CATALOG_FILES=/opt/w3c/catalog.xml
RUN cp -n .env.example .env 2>/dev/null || true; \
    php artisan key:generate --force || true; \
    touch database/database.sqlite && php artisan migrate --force -q || true
