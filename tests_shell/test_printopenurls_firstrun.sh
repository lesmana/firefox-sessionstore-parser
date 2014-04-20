#! /bin/sh

testname="$0.d"
rm -rf "$testname"
mkdir "$testname"
cd "$testname"

sessionstoreparser ../sessionstore.js_firstrun > output
echo $? > exitstatus

cat << EOF > expectedoutput
about:startpage
EOF
echo 0 > expectedexitstatus

diff -u output expectedoutput &&
diff -u exitstatus expectedexitstatus
