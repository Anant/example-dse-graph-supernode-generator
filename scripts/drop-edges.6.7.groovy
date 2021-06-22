// for DSE 6.7
// drops 100,000 edges, the max
:remote config alias g demo_who_likes_whom.g
sn_uuids = ['0d1dacee-2fa8-4a9c-81a0-7e46809e2e4c', '9e205862-c6b4-410e-ab4e-ef125e59d586', '2d8cc0f2-4fe3-413b-8007-ef931d50bac6', '53eb72bd-7a7a-4ff3-b0de-451eab371b05']
g.V().hasLabel("person").has('uuid', within(sn_uuids)).inE("likes").limit(100000).drop()
