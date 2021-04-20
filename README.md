# Flyer

Flyer is a web app that displays the monthly price list of the common routes. It regularly fetches the data and checks the status
of the flights from the external API (or you can do so manually).

## Getting Started Locally

You need to have [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)
installed on your computer to run the app.

To start the app, run the following from the root of the repo:

```sh
docker-compose up --build
```

Then, send a POST request to [http://localhost:1337/fetch/](http://localhost:1337/fetch/) to manually fetch the data of the flights
(it's scheduled to be regularly called every day at midnight, but in the beginning you might need it to populate the DB).

Note that it might take a few minutes for this task to fully complete, but you shouldn't worry about it because it is done async in the background.
You can check the status of the tasks at the dashboard here [http://localhost:5555/](http://localhost:5555/).

Finally, open [http://localhost:1337/api/](http://localhost:1337/api/) to see the cheapest flights for the next month.

### Accessing Admin

You can do many more (see the celery tasks running, schedule of periodic tasks, access the DB, etc.) in the admin pages. <br>
First, let's create a superuser to do that:
```sh
docker-compose exec web python manage.py createsuperuser
```
Then open [http://localhost:1337/admin/](http://localhost:1337/admin/) and enter the credentials of the superuser you just created.

### Fetching and Checking the Flights

Fetching the flights' data is scheduled to happen automatically every day at midnight. Or you can do
it manually at [http://localhost:1337/fetch/](http://localhost:1337/fetch/).

Checking the status of the flights (for a validity or a possible price change) is scheduled to happen
every 3 hours. You can also call it manually at [http://localhost:1337/check/](http://localhost:1337/check/).

## Technologies Used

- **Django and DRF:** The main web-frameworks the app uses to produce RESTful APIs.

- **Celery and Celery Beat:** Celery is used to asynchronously execute IO bound work in the background. Celery Beat is
  used as a scheduler so that tasks are automatically run regularly.

- **Redis:** Redis is used as a message broker between Celery workers and web application.

- **Poetry:** Dependency manager for Python projects.

- **Docker and Docker Compose:** Used to containerize the apps and tie everything together.

Python 3.9.2 is the default language of the project.

## Improvements

The app far from being ready to be deployed to production. Following is the list of main improvements I would work on before releasing:

- Frontend part (probably with React).
- Divide the IO bound tasks to multiple isolated parts so that multiple celery workers can pick them up and run concurrently.
- Add tests and use TDD approach.

## Raising Issues

At the time of writing this, everything was working perfectly on my computer. That being said, I understand some
might face unexpected errors or difficulties to run the app eventually.

So please feel free to raise an issue with the problem that you faced (I'll answer all of them) or contact me via
[email](mailto:madibekov.nurbakhyt@gmail.com).
