# Update your no-ip.com domain name --- Dockerized

This is an update, inspired by the original work of the author, to update the IP binded to a [NO-IP domain](www.noip.com).
I'm not sure how muh this repo has diverted from its original impolementation, but the original author's work inspired all this.

NOTE: Confirming your host each moenth through API is not possible anymore. This code only focuses on updating the IP.


### Build

Just run the provided build file:

```sh
chmod +x ./build.sh
./build.sh
```

### Run

To run a test simply do:

```sh
docker run \
	-v ./untracked:/output \
	-e NOIP_HOSTNAMES=<your_list_of, comma_separated, hostnames> \
	-e NOIP_USERNAME=<your_noip_username> \
	-e NOIP_PASSWORD=<your_noip_password> \
	-e NOIP_LOGLEVEL=DEBUG \
	-it noip_check_update:latest
```

this will create a `log.txt` inside a folder called `untracked` (that should exist).


### Crontab

This is designed to work with a k8s cronjob. Here is a sample of how to create the job that runs every hour.
Please note that this job depends on a `configmap.yaml` and a `secret.yaml` that are not provided (they only include personal data) and a `pv.yaml` that is also not provided (use what you feel like).

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: noip-updater
spec:
  schedule: "0 * * * *"
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 3
  jobTemplate:
    spec:
      template:
        spec:
          restartPolicy: Never
          containers:
          - name: noip-updater
            image: rawthil/noip_check_update:latest
            imagePullPolicy: Always
            env:
              - name: NOIP_LOGLEVEL
                valueFrom:
                  configMapKeyRef:
                    name: noip-updater-config
                    key: loglevel
              - name: NOIP_HOSTNAMES
                valueFrom:
                  secretKeyRef:
                    name: noip-updater-secret
                    key: hostnames
              - name: NOIP_USERNAME
                valueFrom:
                  secretKeyRef:
                    name: noip-updater-secret
                    key: username
              - name: NOIP_PASSWORD
                valueFrom:
                  secretKeyRef:
                    name: noip-updater-secret
                    key: password
            volumeMounts:
            - name: data-disk
              subPath: noip-updates
              mountPath: /output
          volumes:
          - name: data-disk
            persistentVolumeClaim:
              claimName: data-pvc
          - name: tz-config
            hostPath:
              path: /usr/share/zoneinfo/America/Argentina/Buenos_Aires
          

```

