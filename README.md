# hop-plugin-parent

Shared Maven parent POM for Apache Hop plugin repositories. It centralizes the build configuration
that every plugin otherwise repeats and wires the
[hop-plugin-doclint-maven-plugin](https://github.com/edigonzales/hop-plugin-doclint-maven-plugin)
into the `verify` phase.

## Managed by the parent

- Java 21 (`maven.compiler.release`), UTF-8 source encoding
- Apache Hop version `2.19.0` plus JUnit/AssertJ versions
- Versions for Maven Compiler, Surefire, Jar, Assembly and Jandex
- `dependencyManagement` for `hop-core`, `hop-engine`, `hop-ui`, JUnit 5 and AssertJ
- Repositories, plugin repositories and `distributionManagement` for
  `https://jars.interlis.guru/{releases,snapshots}/`
- macOS profiles that set `ui.test.argLine=-XstartOnFirstThread` for SWT tests
- The DocLint execution `validate-hop-plugin-documentation` bound to `verify`

## Usage

A plugin repository only declares the parent and its own specifics:

```xml
<parent>
  <groupId>ch.so.agi</groupId>
  <artifactId>hop-plugin-parent</artifactId>
  <version>0.1.0-SNAPSHOT</version>
  <relativePath/>
</parent>

<artifactId>hop-geometry-calculator-plugin-parent</artifactId>
<packaging>pom</packaging>

<modules>
  <module>hop-geometry-calculator-core</module>
  <module>hop-transform-geometry-calculator</module>
  <module>assemblies</module>
</modules>
```

`<relativePath/>` forces resolution from the Maven repository; the repositories and plugin
repositories inherited from this parent provide the snapshot coordinates while the parent itself is
still a snapshot.

Adopting the parent activates the documentation checks for the whole repository. Repositories
should switch only once their `docs/` and `examples/` are in place, or disable the execution as
described below.

## DocLint

`mvn verify` runs the documentation contract checks in every module. Modules without Hop plugin
annotations (core libraries, assemblies) are skipped automatically, and `docs/`/`examples/` are
resolved against the top-level project.

Skipping the checks for one build:

```bash
mvn verify -Dhop.plugin.doclint.skip=true
```

Skipping them for a repository that deliberately does not follow the contract:

```xml
<plugin>
  <groupId>ch.so.agi</groupId>
  <artifactId>hop-plugin-doclint-maven-plugin</artifactId>
  <executions>
    <execution>
      <id>validate-hop-plugin-documentation</id>
      <phase>none</phase>
    </execution>
  </executions>
</plugin>
```

See the [plugin documentation](https://github.com/edigonzales/hop-plugin-doclint-maven-plugin) for
the check catalogue and parameters.

## Build and local development

```bash
mvn clean package
```

The parent itself has no tests. Because the DocLint execution is bound to `verify`, builds that run
`verify` in this repository also need the DocLint snapshot; use `package` for parent-only work or
install DocLint first.

When DocLint changes locally:

```bash
cd ../hop-plugin-doclint-maven-plugin
mvn install
cd ../hop-plugin-parent
mvn install
```

Publication order is DocLint first, then the parent, so the plugin version referenced here is always
resolvable.

## Publication

Snapshots are published to `https://jars.interlis.guru/snapshots/` through the shared
`hop-plugin-ci` library workflows:

```text
ch.so.agi:hop-plugin-parent:0.1.0-SNAPSHOT
```

Publishing runs on pushes to `main` and manual workflow runs; pull requests verify only. After
publication, `scripts/verify-snapshot.py` resolves the parent in a fresh local repository, builds a
consumer that inherits it and asserts the DocLint execution is present.

## License

MIT
