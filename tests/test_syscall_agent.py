import os
import logging

import angr


test_location = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '..', 'binaries', 'tests')


def test_fauxware(arch="x86_64"):
    p = angr.Project(os.path.join(test_location, arch, "fauxware"),
                     auto_load_libs=True,
                     use_sim_procedures=False,
                     engine=angr.engines.UberEngineSyscallTracing,
                     )
    state = p.factory.full_init_state(add_options={angr.sim_options.ZERO_FILL_UNCONSTRAINED_MEMORY})
    p.bureau.start()
    results = p.factory.simulation_manager(state).explore(find=(0x4006ed, ), avoid=(0x4006aa,0x4006fd, ))
    stdin = results.found[0].posix.dumps(0)
    assert b'\x00\x00\x00\x00\x00\x00\x00\x00\x00SOSNEAKY\x00' == stdin


def test_dir(arch="x86_64"):
    p = angr.Project(os.path.join(test_location, arch, "dir_gcc_-O0" if arch == "x86_64" else "dir"),
                     auto_load_libs=True,
                     use_sim_procedures=False,
                     engine=angr.engines.UberEngineSyscallTracing,
                     )
    p.bureau.start()
    state = p.factory.full_init_state(add_options={angr.sim_options.ZERO_FILL_UNCONSTRAINED_MEMORY} | angr.sim_options.unicorn)
    results = p.factory.simulation_manager(state).explore()
    assert len(results.deadended) == 1


def test_busybox(arch="mips"):
    p = angr.Project(os.path.join(test_location, arch, "busybox"),
                     auto_load_libs=True,
                     use_sim_procedures=False,
                     engine=angr.engines.UberEngineSyscallTracing,
                     )
    state = p.factory.full_init_state(
        add_options={angr.sim_options.ZERO_FILL_UNCONSTRAINED_MEMORY} | angr.sim_options.unicorn,
        args=["ls", "."],
    )
    p.bureau.start()
    results = p.factory.simulation_manager(state).explore()
    assert len(results.deadended) == 1
    print(results.deadended[0].posix.dumps(1))
    print(results.deadended[0].posix.dumps(2))

if __name__ == "__main__":
    logging.getLogger("angr.bureau.bureau").setLevel(logging.DEBUG)
    test_busybox(arch="mips")
    # test_fauxware("mips")