# Repository instructions

## CI and tests

Before changing pipelines or test setup, read the
[shared CI contract](https://github.com/edigonzales/hop-plugin-ci/blob/main/docs/ci-contract.md).
The documentation follows `main`; use the interfaces at this repo's actual workflow/helper
revisions and preserve existing pins and `ci-ref` values.

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

For compatibility use `clean test` instead. This repository publishes a `pom` artifact only; it has
no tests. Builds that reach the `verify` phase also execute the inherited DocLint goal and therefore
need a published DocLint snapshot. Publish DocLint before this parent.

### After snapshot publication only

```bash
python3 scripts/verify-snapshot.py
```

This requires Maven, JDK 21 and network access to the published snapshot matching the root POM
version. It creates a fresh temporary Maven repository, resolves `ch.so.agi:hop-plugin-parent` in a
consumer project, runs `clean verify` and asserts that the inherited DocLint execution is present
and skips the modular consumer classes. It does not validate an unpublished local build and is not a
standard local test command. The workflow runs it after snapshot deployment, allowed on main pushes
and manual runs on main, after verify succeeds.
