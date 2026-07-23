## Automated tests that need to be written

- [ ] Test changing control scheme (`set_control_scheme` - should we remove from Environment class?)
- [ ] Test every control scheme for every agent (many are untested right now)
- [ ] `set_physics_state()`
- [X] rotating the camera
- [X] validate rotation order of various commands
- [X] placing sensors with a rotation
- [ ] placing sensors with a location 
- [ ] placing sensors in sockets
- [ ] Test every sensor on every agent (rewrite individual sensor tests to be more generalizable?) 
- [ ] Test `ticks_per_second` (making simulation longer)
- [ ] test_joint_rotation_sensor could be parameterized instead of looping over an array
- [ ] `has_camera` - do we even need this?
- [ ] Test tagging an prop and using it in a task