# Gremlin Attacks

This is a Python script for scheduling different attacks on our system using Gremlin API. Everything in this script is automated and there is no need to provide any input params.

# Installation

## Install virtualenv and activate it.

```bash
virtualenv venv
source venv/bin/activate
```

## Use the package manager [pip3](https://pip.pypa.io/en/stable/) to install all dependencies.

```bash
pip3 install -r requirements.txt
```

# API

## Create an object of the GremlinAttacks class

```bash
gremlin = GremlinAttacks()
```

## CPU ATTACKS

```bash
gremlin.cpuAttack()
```

### Input param:

```bash
cpu percentage (1-100)
duration of attack in seconds
```
### Output:

```bash
response-id
```

## MEMORY ATTACKS

```bash
gremlin.memoryAttack()
```

### Input param:

```bash
memory in GB
duration of attack in seconds
```
### Output:

```bash
response-id
```