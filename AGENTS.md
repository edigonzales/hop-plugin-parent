# Repository instructions

## CI and tests

Before changing pipelines or test setup, read the
[shared CI contract](https://github.com/edigonzales/hop-plugin-ci/blob/main/docs/ci-contract.md).
Use the CI interfaces at the shared workflow pin.

Run the commands below from this repository root in Bash, using Python 3, Maven and JDK 21
(`JAVA_HOME` and `PATH` pointing to that JDK). Compatibility jobs also use JDK 25. Set
`HOP_CI_DIR` to an absolute checkout of `hop-plugin-ci` at the helper revision used by this repo's
workflow, then prepare the same Maven repositories as CI:

```bash
CI_TEST_TMP="$(mktemp -d)"
export MAVEN_SETTINGS="$CI_TEST_TMP/maven-settings.xml"
python3 "$HOP_CI_DIR/scripts/write_maven_settings.py" --output "$MAVEN_SETTINGS"
```

### Library verification

See [.github/workflows/maven.yml](.github/workflows/maven.yml). The canonical cell is Ubuntu/JDK 21.

```bash
mvn -s "$MAVEN_SETTINGS" -U -B -ntp clean package
```

For compatibility use `clean test`. Run a real consumer build to check changes
to inherited configuration. Install the parent in the same Maven local repository first.
