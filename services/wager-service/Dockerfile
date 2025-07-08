# PHP 8.2 with FPM for Symfony
FROM php:8.2-fpm-alpine

# Install system dependencies
RUN apk add --no-cache \
    nginx \
    supervisor \
    curl \
    git \
    zip \
    unzip \
    bash \
    $PHPIZE_DEPS \
    openssl-dev \
    autoconf \
    g++ \
    make

# Install PHP extensions
RUN docker-php-ext-install pdo pdo_mysql opcache

# Install MongoDB extension
RUN pecl install mongodb && docker-php-ext-enable mongodb

# Install APCu
RUN pecl install apcu && docker-php-ext-enable apcu

# Install Composer
COPY --from=composer:latest /usr/bin/composer /usr/bin/composer

# Configure PHP
COPY docker/php/php.ini /usr/local/etc/php/conf.d/custom.ini

# Configure FPM
COPY docker/php/www.conf /usr/local/etc/php-fpm.d/www.conf

# Configure nginx
COPY docker/nginx/default.conf /etc/nginx/http.d/default.conf

# Configure supervisor
COPY docker/supervisor/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Create app directory
WORKDIR /var/www

# Copy composer files first for better caching
COPY composer.json ./

# Set composer env to avoid memory issues
ENV COMPOSER_MEMORY_LIMIT=-1

# Install dependencies
RUN composer install --no-scripts --no-autoloader --prefer-dist --no-dev --ignore-platform-req=ext-mongodb

# Copy application files
COPY . .

# Generate autoloader
RUN composer dump-autoload --optimize

# Create necessary directories and set permissions
RUN mkdir -p var/cache var/log public/bundles /var/log/php var/cache/doctrine/odm/mongodb/Hydrators \
    && chown -R www-data:www-data var /var/log/php \
    && chmod -R 775 var /var/log/php

# Set environment to production
ENV APP_ENV=prod

# Install assets and clear cache
RUN php bin/console assets:install --env=prod --no-debug \
    && php bin/console cache:clear --env=prod --no-debug

# Copy entrypoint script
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Expose port
EXPOSE 8085

# Start supervisor via entrypoint
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]