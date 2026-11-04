from lib.ctl import folder


def link(ident):
    return {"type": "ccmLink", "id": ident}


def links(idents):
    return [link(ident) for ident in idents]


def buildGm():
    """GM1 and GM2 share one folder. Their controls are defined once under Controls,
    this only gathers them the way the GS and XG folders do: system, then effects."""
    return {
        "tables": [],
        "items": [
            folder(
                "General MIDI",
                [
                    folder(
                        "GM System",
                        links([200, 201, 202])
                        + [folder("Device Control (14 bit)", links([170, 171, 172, 173]))],
                    ),
                    folder("GM2 Effects", links([210, 211, 212, 213, 214, 215, 216])),
                ],
            )
        ],
    }
