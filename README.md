Reference Release Task
======================

This is a minimal task that follows the [Task Service Spec](https://github.com/kids-first/kf-api-release-coordinator)
of the release coordinator service.

## Getting Started

The suggested mode of development is to put up a Coordinator service on a
development machine that the task services may run against:
```
git clone git@github.com:kids-first/kf-api-release-coordinator.git
cd kf-api-release-coordinator
docker-compose up -d
```

Once the coordinator is up, the task service may be brought up with
docker-compose. The compose file will set up the task api, task worker,
and a redis broker and join them to the coordinator network above so that
they may communicate.
```
docker-compose up
```

The task service here may now be registered in the Coordinator at the
`task:8282` endpoint and triggered by issueing a new release.

To use the Coordinator dashboard to register a new task and issue releases,
follow the directions on the [UI repo](https://github.com/kids-first/kf-ui-release-coordinator)


## Release Process

### Recieve `initialize` action

At the begining of a release, the Coordinator will issue an `initialize`
request to the task service. The service is expected to store the `task_id`
and `release_id` for further reference and respond with a state
of `pending` and a response code of `200` indicating that the service is ready
to begin the release process. Any other respose will cause the release to fail
and end immediately.


### Recieve `start` action

After checking all services have replied positively to the `initialize` action,
the Coordinator will issue a `start` action to the service. The service will
reply to the request with an updated state of `running`. The task service
will continue to process and do whatever work is required to prepare a release.
None of these actions should result in public changes such as renaming live
files or adding new participants to the public portal.

### Complete `running`

When the task has completed it's processing, it moves into the `staged` state
and let's the coordinator know of its new status.

### Recieve `publish` action

Once the Coordinator has recieved notifications that all tasks have reached the
`staged` state, a `publish` action will be dispatched and the task will enter
the `publishing` state. During this period, the task will do work to make
the results of the task public for that release.

### Complete `publishing`

When the task has finished `publishing`, it will notify the Coordinator that
the task has been `published` and set its state appropriately.

### Recieve `cancel` action

If a task recieves the `cancel` action, it may assume that the release will
have no further processing. It may discard any work that has been done, if
desired.
