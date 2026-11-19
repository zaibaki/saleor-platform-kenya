![Saleor Platform](https://user-images.githubusercontent.com/249912/71523206-4e45f800-28c8-11ea-84ba-345a9bfc998a.png)

<div align="center">
  <h1>Saleor Platform</h1>
</div>

<div align="center">
  <p>Run all Saleor services from one repository.</p>
</div>

<div align="center">
 Get to know Saleor: <br>
  <a href="https://saleor.typeform.com/talk-with-us?utm_source=github&utm_medium=readme&utm_campaign=repo_platform">Talk to a human</a>
  <span> | </span>
  <a href="https://cloud.saleor.io/signup?utm_source=github&utm_medium=readme&utm_campaign=repo_platform">Talk to the API</a>
</div>

<br>

<div align="center">
  <a href="https://saleor.io/">🏠 Website</a>
  <span> • </span>
  <a href="https://docs.saleor.io/docs/3.x/">📚 Docs</a>
  <span> • </span>
  <a href="https://saleor.io/blog/">📰 Blog</a>
  <span> • </span>
  <a href="https://twitter.com/getsaleor">🐦 Twitter</a>
</div>

<div align="center">
  <a href="https://githubbox.com/saleor/saleor-platform">🔎 Explore Code</a>
</div>

## About

### What is Saleor Platform?

Saleor Platform is the easiest way to start local development with all the major Saleor services:
- [Core GraphQL API](https://github.com/saleor/saleor)
- [Dashboard](https://github.com/saleor/saleor-dashboard)
- Mailpit (Test email interface)
- Jaeger (APM)
- The necessary databases, cache, etc.

*Keep in mind this repository is for local development only and is not meant to be deployed in any production environment! If you're not a developer and just want to try out Saleor you can check our [live demo](https://demo.saleor.io/).*

## Requirements
1. [Docker](https://docs.docker.com/install/)

## How to clone the repository?

To clone the repository, run the following command

```
git clone https://github.com/saleor/saleor-platform.git
```

## How to run it?

1. Project is using shared folders to enable live code reloading. For `macOS` and `Windows` users following steps are required to run `Docker compose`:
    - Add the cloned `saleor-platform` directory to Docker shared directories (Preferences -> Resources -> File sharing).
    - In Docker preferences dedicate at least 5 GB of memory (Preferences -> Resources -> Advanced).


2. Go to the cloned directory:
```shell
cd saleor-platform
```

3. Apply Django migrations:
```shell
docker compose run --rm api python3 manage.py migrate
```

4. Populate the database with example data and create the admin user:
```shell
docker compose run --rm api python3 manage.py populatedb --createsuperuser
```
*Note that `--createsuperuser` argument creates an admin account for `admin@example.com` with the password set to `admin`.*

5. Run the application:
```shell
docker compose up
```

## Where is the application running?
- Saleor Core (API) - http://localhost:8000
- Saleor Dashboard - http://localhost:9000
- Jaeger UI (APM) - http://localhost:16686
- Mailpit (Test email interface) - http://localhost:8025

# Troubleshooting

- [How to solve issues with lack of available space or build errors after an update](#how-to-solve-issues-with-lack-of-available-space-or-build-errors-after-an-update)
- [How to run application parts?](#how-to-run-application-parts)

## How to solve issues with lack of available space or build errors after an update

Most of the time both issues can be solved by cleaning up space taken by old containers. After that, we build again whole platform. 


1. Make sure docker stack is not running
```shell
docker compose stop
```

2. Remove existing volumes

**Warning!** Proceeding will remove also your database container! If you need existing data, please remove only services that cause problems! https://docs.docker.com/compose/reference/rm/
```shell
docker compose rm
```

3. Build fresh containers 
```shell
docker compose build
```

4. Now you can run a fresh environment using commands from `How to run it?` section. Done!

### Still no available space

If you are getting issues with lack of available space, consider pruning your docker cache:

**Warning!** This will remove:
  - all stopped containers
  - all networks not used by at least one container
  - all dangling images
  - all dangling build cache 
  
  More info: https://docs.docker.com/engine/reference/commandline/system_prune/
  
<details><summary>I've been warned</summary>
<p>

```shell
docker system prune
```

</p>
</details>

### Issues with migrations after changing the versions - resetting the database

Please submit an issue ticket if you spot issues with database migrations during the version update. 

When testing developer releases or making local changes, you might end up in a state where you would like to reset the database completely. Since its state is persisted in the mounted volume, you'll need to use a dedicated command.

**Warning!** This command will remove all data already stored in the database.

<details><summary>I've been warned</summary>
<p>

```shell
docker compose down --volumes db
```

</p>
</details>
   
## How to run application parts?
  - `docker compose up api worker` for backend services only
  - `docker compose up` for backend and frontend services

## Feedback

If you have any questions or feedback, do not hesitate to contact us via [GitHub Discussions](https://github.com/saleor/saleor/discussions).

## License

Disclaimer: Everything you see here is open and free to use as long as you comply with the [license](https://github.com/saleor/saleor-platform/blob/main/LICENSE). There are no hidden charges. We promise to do our best to fix bugs and improve the code.

Some situations do call for extra code; we can cover exotic use cases or build you a custom e-commerce appliance.

#### Crafted with ❤️ by [Saleor Commerce](https://saleor.io/)

hello@saleor.io

## Kenya (KES) store

This fork adds a Kenyan storefront dataset on top of the upstream demo data:

- Channel `kenya-kes` ("Kenya (KES)", currency KES, default country KE).
- Category `kenyan-goods` ("Kenyan Goods") with 10 products (SKUs KE-001–KE-010),
  priced in KES and stocked (50 units each) in the `africa` warehouse.
- Collections `featured-products` and `summer-picks` are ensured to exist;
  the Kenyan products are not assigned to any collection.

### How to run

1. Set your own secrets first. `backend.env`, `docker-compose.yml` and
   `replica_user.sql` ship with `REPLACE_WITH_YOUR_OWN_RANDOM_SECRET`
   placeholders instead of real credentials. Replace every placeholder with
   your own random value:
   - `SECRET_KEY` in `backend.env`
   - the password inside `DATABASE_URL` in `backend.env` (same value as
     `POSTGRES_PASSWORD`)
   - `POSTGRES_PASSWORD` in `docker-compose.yml`
   - the `saleor_read_only` password in `replica_user.sql`
2. Start the stack and populate the demo data:
   ```shell
   docker compose up -d
   docker compose exec api python manage.py populatedb
   ```
3. Add the Kenyan channel and products:
   ```shell
   docker cp scripts/seed-kenya.py saleor-platform-api-1:/tmp/seed-kenya.py
   docker exec saleor-platform-api-1 python manage.py shell \
       -c "exec(open('/tmp/seed-kenya.py').read())"
   ```
   The script is idempotent and can be re-run safely.
4. Open the Dashboard at http://localhost:9000 and the API at
   http://localhost:8000/graphql. Demo login: `admin@example.com` / `admin`.

The companion storefront lives in a separate repository and defaults to the
`kenya-kes` channel, so prices render in KES.

### Notes

- The Kenyan data lives in the database, not in this repo's files, except for
  `scripts/seed-kenya.py`, which recreates it from scratch.
- Shipping zones, taxes and payment settings are the upstream demo ones;
  no Kenya-specific shipping zone is configured.
