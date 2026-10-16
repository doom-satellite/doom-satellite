module DoomCoprocessor {

  # ----------------------------------------------------------------------
  # Symbolic constants for port numbers
  # ----------------------------------------------------------------------

  enum Ports_RateGroups {
    rateGroup1Hz
  }

  deployment topology DoomCoprocessor {

  # ----------------------------------------------------------------------
  # Instances used in the topology. The DOOM engine, downsampler and frame telemetry run on DoomFlight; this
  # deployment is the remote end of DoomFlight's GenericHub (commands in, events out).
  # ----------------------------------------------------------------------
    instance cmdDisp
    instance chronoTime
    instance hub
    instance hubComDriver
    instance hubByteStreamAdapter
    instance hubBufferManager
    instance rateGroup1Hz
    instance rateGroupDriver
    instance linuxTimer

  # ----------------------------------------------------------------------
  # Pattern graph specifiers
  # ----------------------------------------------------------------------

    command connections instance cmdDisp

    # Events go to the control node (DoomFlight) over the hub. The hub transport chain (hubByteStreamAdapter,
    # hubBufferManager, hubComDriver) is excluded: its events would re-enter the hub they report on.
    event connections instance hub {
      cmdDisp
      rateGroup1Hz
    }

    time connections instance chronoTime

  # ----------------------------------------------------------------------
  # Direct graph specifiers
  # ----------------------------------------------------------------------

    connections RateGroups {
      linuxTimer.CycleOut -> rateGroupDriver.CycleIn

      rateGroupDriver.CycleOut[Ports_RateGroups.rateGroup1Hz] -> rateGroup1Hz.CycleIn
      rateGroup1Hz.RateGroupMemberOut[0] -> hubBufferManager.schedIn
    }

    connections HubCommands {
      hub.cmdDispOut -> cmdDisp.seqCmdBuff
      cmdDisp.seqCmdStatus -> hub.cmdRespIn
    }

    connections Hub {
      # Hub -> adapter -> UDP (send)
      hub.toBufferDriver                      -> hubByteStreamAdapter.bufferIn
      hubByteStreamAdapter.bufferInReturn     -> hub.toBufferDriverReturn
      hubByteStreamAdapter.toByteStreamDriver -> hubComDriver.$send

      # UDP -> adapter -> hub (receive)
      hubComDriver.$recv                              -> hubByteStreamAdapter.fromByteStreamDriver
      hubByteStreamAdapter.fromByteStreamDriverReturn -> hubComDriver.recvReturnIn
      hubByteStreamAdapter.bufferOut                  -> hub.fromBufferDriver
      hub.fromBufferDriverReturn                      -> hubByteStreamAdapter.bufferOutReturn
      hubComDriver.ready                              -> hubByteStreamAdapter.byteStreamDriverReady

      # Shared buffer allocation
      hub.allocate            -> hubBufferManager.bufferGetCallee
      hub.deallocate          -> hubBufferManager.bufferSendIn
      hubComDriver.allocate   -> hubBufferManager.bufferGetCallee
      hubComDriver.deallocate -> hubBufferManager.bufferSendIn
    }
  }
}
