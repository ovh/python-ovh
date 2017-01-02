#!/bin/bash
#
# Usage: ./scripts/update-copyright.sh
#

PCRE_MATCH_COPYRIGHT="Copyright \(c\) 2013-[0-9]{4}, OVH SAS."
PCRE_MATCH_DEBIAN="Copyright: [-0-9]* OVH SAS"
YEAR=$(date +%Y)

echo -n "Updating copyright headers to ${YEAR}... "
grep -rPl "${PCRE_MATCH_COPYRIGHT}" | xargs sed -ri "s/${PCRE_MATCH_COPYRIGHT}/Copyright (c) 2013-${YEAR}, OVH SAS./g"
grep -rPl "${PCRE_MATCH_DEBIAN}"    | xargs sed -ri "s/${PCRE_MATCH_DEBIAN}/Copyright: 2013-${YEAR} OVH SAS/g"
echo "[OK]"

