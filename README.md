# hop-plugin-parent

Shared Maven build configuration for Apache Hop plugins.

## Managed by the parent

- Java 21 (`maven.compiler.release`), UTF-8 source encoding
- Apache Hop version `2.19.0` plus JUnit/AssertJ versions
- Versions for Maven Compiler, Surefire, Jar, Assembly and Jandex
- `dependencyManagement` for `hop-core`, `hop-engine`, `hop-ui`, JUnit 5 and AssertJ
- Repositories and `distributionManagement` for
  `https://jars.interlis.guru/{releases,snapshots}/`
- macOS profiles that set `ui.test.argLine=-XstartOnFirstThread` for SWT tests

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

`<relativePath/>` resolves the parent by its Maven coordinates. Configure the
snapshot repository in the consumer POM or Maven settings.

## Local development

Install the POM with `mvn install` before testing a consumer locally.

## Publication

Snapshots are published to `https://jars.interlis.guru/snapshots/` through the shared
`hop-plugin-ci` library workflows:

```text
ch.so.agi:hop-plugin-parent:0.1.0-SNAPSHOT
```

Publishing runs on pushes to `main` and manual runs on `main`. Pull requests verify the POM.

## License

MIT
