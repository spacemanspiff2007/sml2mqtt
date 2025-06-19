#!/bin/ash

set -euo pipefail

NEW_USER_ID="${USER_ID}"
NEW_GROUP_ID="${GROUP_ID:-$NEW_USER_ID}"

echo "Starting sml2mqtt with user id: $NEW_USER_ID and group id: $NEW_GROUP_ID"
if ! id -u sml2mqtt >/dev/null 2>&1; then
  if [ -z "$(getent group "${NEW_GROUP_ID}")" ]; then
    echo "Create group sml2mqtt with id ${NEW_GROUP_ID}"
    addgroup -g "${NEW_GROUP_ID}" sml2mqtt
  else
    group_name=$(getent group "${NEW_GROUP_ID}" | cut -d: -f1)
    echo "Rename group $group_name to sml2mqtt"
    groupmod --new-name sml2mqtt "${group_name}"
  fi
  echo "Create user sml2mqtt with id ${NEW_USER_ID}"
# -u UID          User id
# -D              Don't assign a password
# -g GECOS        GECOS field
# -H              Don't create home directory
# -G GRP          Group
  adduser -u "${NEW_USER_ID}" -D -g '' -H -G sml2mqtt sml2mqtt
fi

chown -R sml2mqtt:sml2mqtt "${SML2MQTT_FOLDER}"
sync

exec "$@"
