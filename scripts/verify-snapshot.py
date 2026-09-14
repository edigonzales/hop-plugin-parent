#!/usr/bin/env python3
"""Resolve the published parent POM through Maven and build a consumer with it."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NS = "{http://maven.apache.org/POM/4.0.0}"
VERSION = ET.parse(ROOT / "pom.xml").getroot().find(NS + "version").text
GROUP_ID = "ch.so.agi"
ARTIFACT_ID = "hop-plugin-parent"
# Override for local dry-runs against a file-based repository; CI uses the public snapshot repository.
REPOSITORY_URL = os.environ.get(
    "HOP_PLUGIN_PARENT_REPOSITORY", "https://jars.interlis.guru/snapshots/"
)
DOCLINT_PLUGIN = "hop-plugin-doclint-maven-plugin"


def maven_command(settings: Path, local_repository: Path, *arguments: str) -> list[str]:
    return [
        "mvn",
        "-U",
        "-B",
        "-ntp",
        "-s",
        str(settings),
        "-gs",
        str(settings),
        f"-Dmaven.repo.local={local_repository}",
        *arguments,
    ]


def consumer_pom() -> str:
    return f'''<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <parent>
    <groupId>{GROUP_ID}</groupId>
    <artifactId>{ARTIFACT_ID}</artifactId>
    <version>{VERSION}</version>
    <relativePath/>
  </parent>
  <groupId>example</groupId>
  <artifactId>hop-plugin-parent-consumer</artifactId>
  <version>1.0.0</version>
  <repositories>
    <repository>
      <id>sogeo-snapshots</id>
      <url>{REPOSITORY_URL}</url>
      <releases><enabled>false</enabled></releases>
      <snapshots><enabled>true</enabled><updatePolicy>always</updatePolicy></snapshots>
    </repository>
  </repositories>
  <pluginRepositories>
    <pluginRepository>
      <id>sogeo-snapshots</id>
      <url>{REPOSITORY_URL}</url>
      <releases><enabled>false</enabled></releases>
      <snapshots><enabled>true</enabled><updatePolicy>always</updatePolicy></snapshots>
    </pluginRepository>
  </pluginRepositories>
</project>
'''


def write_project(project: Path) -> None:
    source = project / "src/main/java/example/Consumer.java"
    source.parent.mkdir(parents=True)
    source.write_text(
        """package example;

/** Plain consumer class; the inherited DocLint execution must skip this module. */
public final class Consumer {

  private Consumer() {}

  public static String greeting() {
    return "hello";
  }
}
""",
        encoding="utf-8",
    )
    (project / "pom.xml").write_text(consumer_pom(), encoding="utf-8")


def run(cwd: Path, settings: Path, repository: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        maven_command(settings, repository, *arguments),
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="hop-plugin-parent-consumer-") as temporary:
        project = Path(temporary)
        repository = project / "repository"
        settings = project / "settings.xml"
        settings.write_text('<settings xmlns="http://maven.apache.org/SETTINGS/1.0.0"/>\n', encoding="utf-8")
        write_project(project)

        verified = run(project, settings, repository, "clean", "verify")
        if verified.returncode != 0:
            raise AssertionError(
                "Expected the published parent POM to build the consumer project.\n"
                + verified.stdout
                + verified.stderr
            )
        if "No Hop plugin annotations found" not in verified.stdout:
            raise AssertionError(
                "Expected the inherited DocLint execution to scan the consumer classes.\n"
                + verified.stdout
            )
        if "Hop plugin documentation check skipped" not in verified.stdout:
            raise AssertionError(
                "Expected the inherited DocLint execution to skip the consumer module.\n"
                + verified.stdout
            )

        effective = run(
            project,
            settings,
            repository,
            "help:effective-pom",
            "-Doutput=target/effective-pom.xml",
        )
        if effective.returncode != 0:
            raise AssertionError("Could not evaluate the consumer POM.\n" + effective.stdout)
        effective_pom = (project / "target/effective-pom.xml").read_text(encoding="utf-8")
        for marker in ["validate-hop-plugin-documentation", DOCLINT_PLUGIN]:
            if marker not in effective_pom:
                raise AssertionError(
                    f"Missing '{marker}' in the effective POM of the consumer."
                )

        published = sorted(
            (repository / Path(GROUP_ID.replace(".", "/")) / ARTIFACT_ID / VERSION).glob(
                f"{ARTIFACT_ID}-*.pom"
            )
        )
        if not published:
            raise AssertionError(f"Maven did not resolve {GROUP_ID}:{ARTIFACT_ID}:{VERSION}")

    result = {
        "version": VERSION,
        "artifacts": {path.name: "pom" for path in published},
        "doclintExecution": "validate-hop-plugin-documentation",
    }
    (ROOT / "target").mkdir(exist_ok=True)
    (ROOT / "target/published-snapshot.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
