from ciscoconfparse import CiscoConfParse
import logging
import json
import collections
import re
from copy import copy
import sys
from deepmerge import always_merger
from natsort import natsorted
from netaddr import IPNetwork


def tree():
    return collections.defaultdict(tree)


CLIBaseMatrix = {
    r"^(no )?switchport( monitor)?$": None,
    r"^switchport access vlan (\d+)$": None,
    r"^spanning-tree portfast ?(.*)?$": None,
    r"^spanning-tree port type (.*)$": None,
    r"^(no )?spanning-tree bpduguard( \S+)?$": None,
    r"^spanning-tree link-type (\S+)$": None,
    r"^spanning-tree port-priority (\d+)$": None,
    r"^spanning-tree cost (\d+|auto)$": None,
    r"^spanning-tree guard root$": None,
    r"^spanning-tree guard none$": None,
    r"^(no )?spanning-tree bpdufilter( \S+)?$": None,
    r"^(no )?description(.*)$": None,
    r"^dfe-tuning-delay (\d+)$": None,
    r"^(no )?switchport autostate exclude$": None,
    r"^autostate$": None,
    r"^speed (\d+|auto)$": None,
    r"^fec (\S+)$": None,
    r"^duplex (\S+)$": None,
    r"^(no )?shutdown( lan)?$": None,
    r"^(no )?cdp enable$": None,
    r"^(no )?cdp tlv (\S+)$": None,
    r"^switchport port-security$": None,
    r"^switchport trunk allowed vlan (.*)": None,
    r"^switchport mode (\S+)": None,
    r"^(no )?switchport vlan mapping enable$": None,
    r"^mls qos vlan-based": None,
    r"(no )?mls qos channel-consistency": None,
    r"^storm-control (\S+) level (\S+)": None,
    r"^storm-control broadcast include multicast": None,
    r"^(no )?storm-control action ?(\S+)?": None,
    r"^switchport trunk native vlan (\d+)": None,
    r"^ip flow ingress$": None,
    r"^stack-mib portname .*": None,
    r"^switchport trunk encapsulation (\S+)$": None,
    r"^(no )?snmp trap link-status$": None,
    r"^no switchport nonegotiate$": None,
    r"^no switchport protected$": None,
    r"^(no )?switchport block (\S+)$": None,
    r"^no ip arp inspection trust$": None,
    r"^ip arp inspection limit rate (\d+) burst interval (\d+)$": None,
    r"^ip arp inspection limit rate (\d+)$": None,
    r"^(no )?mab$": None,
    r"^snmp trap mac-notification change added$": None,
    r"^snmp trap mac-notification change removed$": None,
    r"^power inline consumption (\d+)$": None,
    r"^power inline auto max (\d+)$": None,
    r"^power inline police$": None,
    r"^ipv6 mld snooping tcn flood$": None,
    r"^ip igmp snooping tcn flood$": None,
    r"^switchport private-vlan trunk encapsulation dot1q$": None,
    r"^switchport private-vlan trunk native vlan tag$": None,
    r"^switchport private-vlan trunk native vlan (\d+)$": None,
    r"^switchport private-vlan trunk allowed vlan none$": None,
    r"^switchport port-security maximum (\d+)$": None,
    r"^switchport port-security maximum (\d+) vlan$": None,
    r"^switchport port-security maximum (\d+) vlan access$": None,
    r"^switchport port-security maximum (\d+) vlan voice$": None,
    r"^switchport port-security aging type (\S+)$": None,
    r"^no switchport port-security$": None,
    r"^switchport port-security aging time (\d+)$": None,
    r"^switchport port-security violation (\S+)$": None,
    r"^switchport port-security aging type absolute$": None,
    r"^switchport port-security limit rate invalid-source-mac (\d+)$": None,
    r"^no switchport port-security mac-address sticky$": None,
    r"^no switchport port-security aging static$": None,
    r"^load-interval (\d+)$": None,
    r"^hold-queue (\d+) out$": None,
    r"^hold-queue (\d+) in$": None,
    r"^lacp port-priority (\d+)$": None,
    r"^lacp rate (\S+)$": None,
    r"^priority-flow-control mode (\S+)$": None,
    r"^(no )?lldp (\S+)$": None,
    r"^(no )?lldp tlv-set management-address (\S+)$": None,
    r"^(no )?lldp tlv-set vlan ?(\S+)?$": None,
    r"^(no )?hardware multicast hw-hash$": None,
    r"^(no )?hardware vethernet mac filtering per-vlan$": None,
    r"^(no )?switchport dot1q ethertype( \S+)?$": None,
    r"^(no )?switchport priority extend( \S+)?( \S+)?$": None,
    r"^flowcontrol (\S+) (\S+)$": None,
    r"^(no )?negotiate auto$": None,
    r"^no link debounce$": None,
    r"linkdebounce time (\d+)": None,
    r"link debounce link-up time (\d+)": None,
    r"^(no )?beacon$": None,
    r"^mtu (\d+)$": None,
    r"^ip mtu (\d+)$": None,
    r"^delay (\d+)$": None,
    r"^log debugging event port link-status default$": None,
    r"^log debugging event port trunk-status default$": None,
    r"^(no )?bandwidth inherit$": None,
    r"^mdix auto$": None,
    r"^load-interval counter (\d+) (\d+)$": None,
    r"^no load-interval counter (\d+)$": None,
    r"^medium (\S+)$": None,
    r"^bandwidth (\d+)$": None,
    r"^(no )?logging event port (link|trunk)-status ?(\S+)?$": None,
    r"^(no )?logging event (link|trunk|bundle)-status$": None,
    r"^link debounce time (\d+)$": None,
    r"^no udld disable$": None,
    r"^channel-group (\d+)( mode )?(\S+)?$": None,
    r"^channel-group auto$": None,
    r"^carrier-delay msec (\d+)$": None,
    r"^carrier-delay (\d+)$": None,
    r"^(no )?mac-address ?(\S+)?$": None,
    r"^no management$": None,
    r"^(no )?ip redirects$": None,
    r"^(no )?ipv6 redirects$": None,
    r"^(no )?ip address ?(\S+)?(/|\ )?(\S+)? ?(secondary)?$": None,
    r"^(no )?lacp suspend-individual$": None,
    r"^(no )?lacp graceful-convergence$": None,
    r"^lacp min-links (\d+)$": None,
    r"^lacp max-bundle (\d+)$": None,
    r"^no port-channel port load-defer$": None,
    r"^lacp fast-select-hot-standby$": None,
    r"^vpc peer-link$": None,
    r"^vpc (\d+)$": None,
    r"^spanning-tree guard loop$": None,
    r"^vtp$": None,
    r"^switchport trunk pruning vlan ((\d+-\d+)|none)$": None,
    r"^fex associate (\d+)$": None,
    r"^standby (\d+) ip (\S+)$": None,
    r"^standby (\d+) priority (\S+)$": None,
    r"^standby (\d+) preempt$": None,
    r"^standby (\d+) preempt delay minimum (\d+)$": None,
    r"^standby (\d+) authentication md5 key-string 7 (\S+)$": None,
    r"^standby (\d+) authentication (\S+)$": None,
    r"^(no )?ip proxy-arp$": None,
    r"^ip igmp snooping querier$": None,
    r"^ip helper-address (\S+)$": None,
    r"^ip access-group (\S+) (\S+)$": None,
    r"^priority-flow-control watch-dog-interval (\S+)": None,
    r"^(no )?dual-active fast-hello": None,
    r"^mls qos trust (\S+)": None,
    r"^udld port (\S+)": None,
    r"^speed nonegotiate": None,
    r"^ip ospf message-digest-key (\d+) (\S+) (\S+) (\S+)": None,
    r"^(no )?ipv6.*": None,
    r"^mls qos cos (\d+)": None,
    r"^(no )?ip unreachables": None,
    r"^(no )?ip route-cache ?(\S+)?": None,
    r"^ip ospf network (\S+)": None,
    r"^ip vrf forwarding (\S+)": None,
    r"^tx-ring-limit (\d+)": None,
    r"^tx-queue-limit (\d+)": None,
    r"^arp arpa$": None,
    r"^arp timeout (\d+)$": None,
    r"^(no )?port-channel port hash-distribution": None,
    r"^(no )?lacp mode delay": None,
    r"^speed auto \d+( \d+)?": None,
    r"^(no )?macsec network-link": None,
    r"^(no )?macsec replay-protection": None,
    r"^(no )?macsec$": None,
    r"^(no )?onep application openflow exclusive$": None,
    r"^(no )?mka pre-shared-key$": None,
    r"^(no )?mka default-policy$": None,
    r"^(no )?channel-protocol lacp$": None,
    r"^cts role-based enforcement$": None,
    r"^evc-lite bridge-domain (\d+)$": None,
    r"^(no )?ip dhcp snooping information option (\S+)$": None,
    r"^ip dhcp snooping limit rate (\d+)$": None,
    r"^(no )?power inline (\S+)$": None,
    r"^ip load-sharing per-destination$": None,
    r"^ip cef accounting non-recursive internal$": None,
    r"^ip pim join-prune-interval (\d+)$": None,
    r"^ip pim dr-priority (\d+)$": None,
    r"^ip pim query-interval (\d+)$": None,
    r"^ip mfib forwarding (\S+)$": None,
    r"^ip mfib cef (\S+)$": None,
    r"^ip split-horizon$": None,
    r"^ip igmp last-member-query-interval (\d+)$": None,
    r"^ip igmp last-member-query-count (\d+)$": None,
    r"^ip igmp (v3-)?query-max-response-time (\d+)$": None,
    r"^ip igmp version (\d+)$": None,
    r"^ip igmp query-interval (\d+)$": None,
    r"^ip igmp tcn query count (\d+)$": None,
    r"^ip igmp tcn query interval (\d+)$": None,
    r"^no counter$": None,
    r"^mls qos dscp-mutation Default DSCP Mutation Map$": None,
    r"^service-policy (input|output) (\S+)$": None,
    r"^priority-queue out$": None,
    r"^(no )?encapsulation dynamic$": None,
    r"^(no )?ip dhcp snooping trust$": None,
    r"^wrr-queue (\S+) (.*)$": None,
    r"^priority-queue (cos|dscp)-map (.*)$": None,
    r"^rcv-queue dscp-map (.*)$": None,
    r"^mls qos queue-mode mode-dscp$": None,
    r"^priority-queue queue-limit (\d+)": None,
    r"^ip pim sparse-dense-mode": None,
    r"^mpls ip": None,
    r"^spanning-tree mst pre-standard": None,
    r"^ip directed-broadcast$": None,
    r"^ip mobile arp timers (\d+) (\d+)$": None,
    r"^ip cgmp$": None,
    r"^ip policy route-map (\S+)$": None,
    r"^switch virtual link (\d+)$": None,
    r"^vrf forwarding (\S+)$": None,
    r"^vrf member (\S+)$": None,
    r"^(no )?mvrp (.*)$": None,
    r"^no mvrp$": None,
    r"^(no )?switchport trunk native vlan tag": None,
    r"^keepalive (\d+)": None,
    r"^ethernet oam max-rate (\d+)": None,
    r"^ethernet oam min-rate (\d+)": None,
    r"^ethernet oam mtu (\d+)": None,
    r"^ethernet oam remote-loopback timeout (\d+)": None,
    r"^ethernet oam timeout (\d+)": None,
    r"^macro description": None,
    r"^mpls mldp": None,
    r"^mpls mtu (\d+)": None,
    r"^(no )?arp arpa": None,
    r"^(no )?bgp-policy accounting input": None,
    r"^(no )?bgp-policy accounting input source": None,
    r"^(no )?bgp-policy accounting output": None,
    r"^(no )?bgp-policy accounting output source": None,
    r"^(no )?bgp-policy destination ip-prec-map": None,
    r"^(no )?bgp-policy destination ip-qos-map": None,
    r"^(no )?bgp-policy source ip-prec-map": None,
    r"^(no )?bgp-policy source ip-qos-map": None,
    r"^(no )?ip pim snooping": None,
    r"^(no )?platform ip features sequential": None,
    r"^(no )?vtp": None,
    r"^tcam priority": None,
    r"^vslp interval (\d+) min_rx (\d+) multiplier (\d+)": None,
    r"^ip bandwidth-percent eigrp (\d+) (\d+)": None,
    r"^ip hello-interval eigrp (\d+) (\d+)": None,
    r"^ip hold-time eigrp (\d+) (\d+)": None,
    r"^ip next-hop-self eigrp (\d+)": None,
    r"^ip split-horizon eigrp (\d+)": None,
    r"^mpls ldp igp autoconfig": None,
    r"^mpls ldp igp sync": None,
    r"^(no )?ip dampening-change eigrp (\d+)": None,
    r"^(no )?ip dampening-interval eigrp (\d+)": None,
    r"authentication periodic": None,
    r"dot1x pae authenticator": None,
    r"fabricpath isis metric (\d+)": None,
    r"^(no) ?ip port-unreachable": None,
    r"^vpc orphan-port suspend": None,
}


class TargetGeneric(object):
    def __init__(self, parent=None):
        self._log = logging.getLogger()
        self._matrix = copy(CLIBaseMatrix)
        self.registerFunctions()
        self._allKeys = []
        self._parent = parent

    @property
    def matrix(self):
        return self._matrix

    def genFunctionNameFromRgx(self, rgx):
        rgx = str(rgx)
        return (
            rgx.replace("+", "plus")
            .replace(" ", "_")
            .replace("-", "_")
            .replace("\\", "")
            .replace("(", "")
            .replace(")", "")
            .replace("^", "")
            .replace("$", "")
            .replace("?", "opt")
            .replace(".*", "MATCHALL")
            .replace("|", "or")
            .replace("/", "slash")
        )

    def registerFunctions(self):
        for k in self._matrix.keys():
            fnname = self.genFunctionNameFromRgx(k)
            self._log.debug("trying to register: {0}".format(fnname))
            self._matrix[k] = getattr(self, fnname, self._default)
            if self._matrix[k] == self._default:
                self._log.debug(
                    "def {0}(self,data,match,int_obj): not implemented, using default handler".format(
                        fnname
                    )
                )

    def _default(self, data, match, int_obj):
        self._log.warn("default handler used for data: {0}".format(data))
        tmp = data.split(" ")
        val = tmp.pop()
        return {"_".join(tmp): val}

        # sys.exit(0)

    def no_optipv6_MATCHALL(self, data, match, int_obj):
        """ipv6 nd dad attempts 1
            ipv6 nd ns-interval 0
            ipv6 nd nud igp
            ipv6 nd prefix framed-ipv6-prefix
            ipv6 nd ra interval 200
            ipv6 nd ra lifetime 1800
            ipv6 nd reachable-time 0
            no ipv6 nd ra solicited unicast
        """
        self._log.warn("ipv6 commands not implemented: {0}".format(data))

    def mtu_dplus(self, data, match, int_obj):
        return {"mtu": match.group(1)}

    def ip_mtu_dplus(self, data, match, int_obj):
        return {"ip": {"mtu": match.group(1)}}

    def no_switchport_nonegotiate(self, data, match, int_obj):
        return {"dtp": "desi"}  # not sure

    def flowcontrol_Splus_Splus(self, data, match, int_obj):
        if match.group(1).lower() == "receive":
            dir = "rx"
        else:
            dir = "tx"
        if match.group(2).lower() == "on":
            val = True
        else:
            val = False
        return {"flowcontrol": {dir: val}}

    def fex_associate_dplus(self, data, match, int_obj):
        return {"fex": {"id": match.group(1)}}

    def no_optlldp_Splus(self, data, match, int_obj):
        if match.group(1):
            val = False
        else:
            val = True
        if match.group(2).lower() == "transmit":
            dir = "tx"
        elif match.group(2).lower() == "receive":
            dir = "rx"
        return {"lldp": {dir: val}}

    def no_optlldp_tlv_set_management_address_Splus(self, data, match, int_obj):
        if match.group(1):
            val = False
        else:
            val = match.group(2)
        return {"lldp": {"tlv": {"mgmt_addr": val}}}

    def no_optlldp_tlv_set_vlan_optSplusopt(self, data, match, int_obj):
        if match.group(1):
            val = False
        else:
            val = match.group(2)
        return {"lldp": {"tlv": {"vlan": val}}}

    def switchport_mode_Splus(self, data, match, int_obj):
        retval = [{"switchport": {"mode": match.group(1).lower()}}]
        if match.group(1).lower() == "fex-fabric":
            retval.append({"has_fex": True, "isL3": False, "isL2": True})
        if match.group(1).lower() == "trunk":
            retval.append({"isL3": False, "isL2": True})
            if not int_obj.re_search_children("switchport trunk allowed vlan"):
                retval.append({"switchport": {"tagged_vlans": "all"}})
        if match.group(1).lower() == "dynamic":
            retval.append({"switchport": {"dtp": True}, "isL3": False, "isL2": True})
        if match.group(1).lower() == "access":
            retval.append({"isL3": False, "isL2": True})
        return retval

    def switchport_access_vlan_dplus(self, data, match, int_obj):
        res = None
        rgx = self._parent.getRegex(r"switchport mode (\S+)")
        for obj in int_obj.re_search_children(rgx):
            line = obj.text.strip()
            mode_match = self._parent.getRegex(r"^switchport mode (\S+)").match(line)
            res = self.switchport_mode_Splus(line, mode_match, int_obj)
        try:
            if res[0]["switchport"]["mode"] == "access":
                return {"switchport": {"untagged_vlan": match.group(1).lower()}}
        except TypeError:
            return {}
        return {}

    def switchport_trunk_native_vlan_dplus(self, data, match, int_obj):
        rgx = self._parent.getRegex(r"switchport mode (\S+)")
        res = None
        for obj in int_obj.re_search_children(rgx):
            line = obj.text.strip()
            mode_match = self._parent.getRegex(r"^switchport mode (\S+)").match(line)
            res = self.switchport_mode_Splus(line, mode_match, int_obj)
        try:
            if res[0]["switchport"]["mode"] == "trunk":
                return {"switchport": {"untagged_vlan": match.group(1).lower()}}
        except TypeError:
            return {}
        return {}

    def switchport_trunk_allowed_vlan_MATCHALL(self, data, match, int_obj):
        rgx = self._parent.getRegex(r"switchport mode (\S+)")
        res = None
        for obj in int_obj.re_search_children(rgx):
            line = obj.text.strip()
            mode_match = self._parent.getRegex(r"^switchport mode (\S+)").match(line)
            res = self.switchport_mode_Splus(line, mode_match, int_obj)
        try:
            if res[0]["switchport"]["mode"] in ["trunk", "dynamic"]:
                return {"switchport": {"tagged_vlans": match.group(1).lower()}}
        except TypeError:
            return {}
        return {}

    def no_optswitchport_vlan_mapping_enable(self, data, match, int_obj):
        if match.group(1):
            val = False
        else:
            val = True
        return {"switchport": {"vlan_mapping": val}}

    def no_optshutdown_lanopt(self, data, match, int_obj):
        val2 = False
        if match.group(1):
            val = True
            val2 = True
        else:
            val = False
            if match.group(2):
                val2 = False
        return [{"enabled": val}, {"lan_enabled": val2}]

    def no_optdescriptionMATCHALL(self, data, match, int_obj):
        val = None
        if match.group(2):
            val = match.group(2).strip()
        return {"description": val}

    def no_optcdp_enable(self, data, match, int_obj):
        if match.group(1):
            val = False
        else:
            val = True
        return {"cdp": {"enabled": val}}

    def no_optcdp_tlv_Splus(self, data, match, int_obj):
        if match.group(1):
            val = False
        else:
            val = True
        return {"cdp": {"tlv": {match.group(2): val}}}

    def lacp_port_priority_dplus(self, data, match, int_obj):
        return {"lacp": {"priority": match.group(1)}}

    def lacp_rate_Splus(self, data, match, int_obj):
        tmp = match.group(1).lower().strip()
        if tmp == "normal":
            val = False
        elif tmp == "fast":
            val = True
        return {"lacp": {"fast": val}}

    def priority_flow_control_mode_Splus(self, data, match, int_obj):
        tmp = match.group(1).lower().strip()
        if tmp == "auto":
            val = "auto"
        elif tmp == "on":
            val = True
        elif tmp == "off":
            val = False
        return {"pfc": {"mode": val}}

    def priority_flow_control_watch_dog_interval_Splus(self, data, match, int_obj):
        if match.group(1).strip().lower() == "off":
            val = False
        else:
            val = True
        return {"pfc": {"watch_dog_interval": val}}

    def no_optswitchport_block_Splus(self, data, match, int_obj):
        if match.group(1):
            val = False
        else:
            val = True
        return {"switchport": {match.group(2).lower().strip(): {"block": val}}}

    def no_opthardware_multicast_hw_hash(self, data, match, int_obj):
        if match.group(1):
            val = False
        else:
            val = True
        return {"switchport": {"multicast": {"hw-hash": val}}}

    def no_opthardware_vethernet_mac_filtering_per_vlan(self, data, match, int_obj):
        if match.group(1):
            val = False
        else:
            val = True
        return {"switchport": {"vethernet": {"filtering_per_vlan": val}}}

    def no_optswitchport_monitoropt(self, data, match, int_obj):
        retval = []
        if match.group(2) and not match.group(1):
            retval.append({"isMonitoring": True})
        else:
            retval.append({"isMonitoring": False})
        if match.group(1):
            val = False
        else:
            val = True
        retval.append({"isL3": val})
        retval.append({"isL2": not val})
        return retval

    def no_optswitchport_dot1q_ethertype_Splusopt(self, data, match, int_obj):
        if match.group(1):
            val = "0x8100"
        else:
            match.group(2).strip()
        return {"dot1q": {"ethertype": val}}

    def no_optswitchport_priority_extend_Splusopt_Splusopt(self, data, match, int_obj):
        self._log.debug("skipping useless command: {0}".format(data))
        return {}

    def spanning_tree_port_priority_dplus(self, data, match, int_obj):
        return {"stp": {"priority": match.group(1)}}

    def spanning_tree_cost_dplusorauto(self, data, match, int_obj):
        return {"stp": {"cost": match.group(1)}}

    def spanning_tree_link_type_Splus(self, data, match, int_obj):
        return {"stp": {"linkType": match.group(1)}}

    def spanning_tree_port_type_MATCHALL(self, data, match, int_obj):
        return {"stp": {"port_type": match.group(1)}}

    def no_optspanning_tree_bpduguard_Splusopt(self, data, match, int_obj):
        if match.group(1):
            val = False
        else:
            val = True
        try:
            if match.group(2).strip() == "enable":
                val = True
            elif match.group(2).strip() == "disable":
                val = False
        except BaseException:
            pass
        return {"stp": {"bpduguard": val}}

    def no_optspanning_tree_bpduSplusopt(self, data, match, int_obj):
        if match.group(1):
            val = False
        else:
            val = True
        try:
            if match.group(2).strip() == "enable":
                val = True
            elif match.group(2).strip() == "disable":
                val = False
        except BaseException:
            pass
        return {"stp": {"bpdufilter": val}}

    def spanning_tree_guard_loop(self, data, match, int_obj):
        return {"stp": {"loopguard": True}}

    def speed_dplusorauto(self, data, match, int_obj):
        return {"speed": match.group(1)}

    def speed_nonegotiate(self, data, match, int_obj):
        return {"speed_nonegotiate": True}

    def duplex_Splus(self, data, match, int_obj):
        return {"duplex": match.group(1)}

    def no_optnegotiate_auto(self, data, match, int_obj):
        if match.group(1):
            val = False
        else:
            val = True
        return {"autoneg": val}

    def linkdebounce_time_dplus(self, data, match, int_obj):
        return {"debounce": {"timer": match.group(1)}}

    def link_debounce_link_up_time_dplus(self, data, match, int_obj):
        return {"debounce": {"linkUpTimer": match.group(1)}}

    def no_linkdebounce(self, data, match, int_obj):
        return {"debounce": False}

    def no_link_debounce(self, data, match, int_obj):
        return self.no_linkdebounce(data, match, int_obj)

    def link_debounce_time_dplus(self, data, match, int_obj):
        return self.linkdebounce_time_dplus(data, match, int_obj)

    def no_optbeacon(self, data, match, int_obj):
        if match.group(1):
            val = False
        else:
            val = True
        return {"beacon": val}

    def delay_dplus(self, data, match, int_obj):
        return {"delay": match.group(1)}

    def no_optsnmp_trap_link_status(self, data, match, int_obj):
        if match.group(1):
            val = False
        else:
            val = True
        return {"snmp": {"trap": {"link": val}}}

    def no_optlogging_event_port__optlinkortrunkorbundle_status_optSplusopt(
        self, data, match, int_obj
    ):
        val = False
        global_default = False
        if match.group(3).strip() == "enabled":
            val = True
        elif match.group(3).strip() == "default":
            rgx = self._parent.getRegex(
                r"^(no )?logging event {0}-status (\S+)".format(match.group(2).strip())
            )
            cfgs = self._parent._cfg.find_objects(rgx)
            for cfg in cfgs:
                status = cfg.re_match(rgx, 2)
                if status == "default":
                    if not cfg.re_match(rgx):
                        global_default = True
                    else:
                        global_default = False
                if status == "enable":
                    if not cfg.re_match(rgx):
                        global_enable = True
                    else:
                        global_enable = False
            if global_default and global_enable:
                val = True
        return {"logging": {match.group(2).strip(): val}}

    def bandwidth_dplus(self, data, match, int_obj):
        return {"bandwidth": match.group(1).strip()}

    def no_optbandwidth_inherit(self, data, match, int_obj):
        """
        The bandwidth command sets an informational parameter to communicate only the current bandwidth
        to the higher-level protocols; you cannot adjust the actual bandwidth of an interface using this command.
        The bandwidth inherit command controls how a subinterface inherits the bandwidth of its main
        interface.
        The no bandwidth inherit command enables all subinterfaces to inherit the default bandwidth of the
        main interface, regardless of the configured bandwidth. If a bandwidth is not configured on a
        subinterface, and you use the bandwidth inherit command, all subinterfaces will inherit the current
        bandwidth of the main interface. If you configure a new bandwidth on the main interface, all
        subinterfaces will use this new value.
        If you do not configure a bandwidth on the subinterface and you configure the bandwidth inherit
        command on the main interface, the subinterfaces will inherit the specified bandwidth.
        In all cases, if an interface has an explicit bandwidth setting configured, then that interface will use that
        setting, regardless of whether the bandwidth inheritance setting is in effect.
        """
        self._log.debug("not implemented by now")
        return {}

    def mdix_auto(self, data, match, int_obj):
        return {"mdix": "auto"}

    def storm_control_Splus_level_Splus(self, data, match, int_obj):
        return {"storm_control": {match.group(1): match.group(2)}}

    def no_optstorm_control_action_optSplusopt(self, data, match, int_obj):
        if match.group(1):
            val = False
        else:
            val = match.group(2)
        return {"storm_control": {"action": val}}

    def load_interval_counter_dplus_dplus(self, data, match, int_obj):
        return {"load_interval_counter": {match.group(1): match.group(2)}}

    def no_load_interval_counter_dplus(self, data, match, int_obj):
        return {"load_interval_counter": {match.group(1): False}}

    def medium_Splus(self, data, match, int_obj):
        return {"medium": match.group(1)}

    def channel_group_dplus_mode_optSplusopt(self, data, match, int_obj):
        retval = []
        if match.group(2):
            if match.group(3):
                if match.group(3).strip() == "on":
                    lagmode = "static"
                elif match.group(3).strip() == "active":
                    lagmode = "lacp_active"
                elif match.group(3).strip() == "passive":
                    lagmode = "lacp_passive"
        else:
            lagmode = "static"

        rgx = self._parent.getRegex(
            r"^interface port-channel{0}$".format(match.group(1))
        )
        childRgx = self._parent.getRegex(r"vpc (\d+)$")
        cfgs = self._parent._cfg.find_objects(rgx)
        for cfg in cfgs:
            for child in cfg.re_search_children(childRgx):
                m = child.re_match(childRgx, 1)
                if m:
                    retval.append({"is_mlag_interface": True})
                    retval.append({"mlag_id": m})

        retval.append({"parent": match.group(1)})
        retval.append({"is_lag_interface": True})
        retval.append({"lag_mode": lagmode})
        return retval

    def vtp(self, data, match, int_obj):
        return {"vtp": True}

    def switchport_trunk_pruning_vlan_dplus_dplusornone(self, data, match, int_obj):
        # dead command
        self._log.debug("not implemented by now")
        return {}

    def fec_Splus(self, data, match, int_obj):
        return {"fec": match.group(1).lower()}

    def dfe_tuning_delay_dplus(self, data, match, int_obj):
        return {"dfe": {"tuning_delay": match.group(1).lower()}}

    def no_optswitchport_autostate_exclude(self, data, match, int_obj):
        if match.group(1):
            val = False
        else:
            val = True
        return {"switchport": {"autostateexclude": val}}

    def no_optmac_address_optSplusopt(self, data, match, int_obj):
        if match.group(1):
            val = ""
        else:
            val = match.group(2)
        return {"mac": val}

    def no_optip_address_optSplusoptslashor_optSplusopt_optsecondaryopt(
        self, data, match, int_obj
    ):
        prefix = None
        mask = None
        if match.group(5):
            ip_type = "secondary"
        else:
            ip_type = "primary"
        if match.group(1):
            return {"ipv4": {"address": False}}
        add = match.group(2)
        if match.group(4):
            if "." in match.group(4):
                prefix = str(
                    sum(bin(int(x)).count("1") for x in match.group(4).split("."))
                )
                mask = match.group(4)

        return [
            {"ipv4": {add: {"type": ip_type}}},
            {"ipv4": {add: {"prefix": prefix}}},
            {"ipv4": {add: {"netmask": mask}}},
        ]

    # def standby_dplus_priority_Splus(self,data,match,int_obj):
    #     {"ipv4":[{"address":add},{"mask":mask},{"prefix":prefix}]}

    def no_optip_redirects(self, data, match, int_obj):
        if match.group(1):
            val = False
        else:
            val = True
        return {"ipv4": {"send_icmp_redirect": val}}

    def no_optip_unreachables(self, data, match, int_obj):
        if match.group(1):
            val = False
        else:
            val = True
        return {"ipv4": {"send_icmp_unreachable": val}}

    def no_optipv6_redirects(self, data, match, int_obj):
        if match.group(1):
            val = False
        else:
            val = True
        return {"ipv6": {"icmp_redirect": val}}

    def standby_dplus_ip_Splus(self, data, match, int_obj):
        return [{"hsrp": {match.group(1): {"ip": match.group(2).strip()}}}]

    def standby_dplus_authentication_md5_key_string_7_Splus(self, data, match, int_obj):
        return [
            {"hsrp": {match.group(1): {"auth": {"type": "md5"}}}},
            {"hsrp": {match.group(1): {"auth": {"format": "7"}}}},
            {"hsrp": {match.group(1): {"auth": {"key": match.group(1).strip()}}}},
        ]

    def standby_dplus_authentication_Splus(self, data, match, int_obj):
        return [{"hsrp": {match.group(1): {"auth": {"status": match.group(2)}}}}]

    def standby_dplus_preempt_delay_minimum_dplus(self, data, match, int_obj):
        return {
            "hsrp": {match.group(1): {"preempt_delay": {"minimum": match.group(2)}}}
        }

    def standby_dplus_preempt(self, data, match, int_obj):
        return {"hsrp": {match.group(1): {"preempt": True}}}

    def standby_dplus_priority_Splus(self, data, match, int_obj):
        return {"hsrp": {match.group(1): {"priority": match.group(2)}}}

    def no_optip_proxy_arp(self, data, match, int_obj):
        if match.group(1):
            val = False
        else:
            val = True
        return {"proxy_arp": val}

    def ip_helper_address_Splus(self, data, match, int_obj):
        return {"dhcp": {"forward": [match.group(1).strip()]}}

    def ip_igmp_snooping_querier(self, data, match, int_obj):
        return {"igmp": {"snooping_querier": True}}

    def ip_access_group_Splus_Splus(self, data, match, int_obj):
        self._log.error("not fully implemented")
        return {"acl": {match.group(2): match.group(1)}}

    def no_optdual_active_fast_hello(self, data, match, int_obj):
        if match.group(1):
            val = False
        else:
            val = True
        return {"vss": {"dual_active_fast_hello": val}}

    def mls_qos_cos_dplus(self, data, match, int_obj):
        return [{"qos": {"type": "mls"}}, {"qos": {"set_cos": match.group(1).strip()}}]

    def mls_qos_trust_Splus(self, data, match, int_obj):
        return [{"qos": {"type": "mls"}}, {"qos": {"trust": match.group(1).strip()}}]

    def no_optmab(self, data, match, int_obj):
        if match.group(1):
            val = False
        else:
            val = True
        return {"dot1x": {"mab": val}}

    def switchport_trunk_encapsulation_Splus(self, data, match, int_obj):
        return {"switchport": {"trunk_encapsulation": match.group(1)}}

    def spanning_tree_portfast_optMATCHALLopt(self, data, match, int_obj):
        try:
            if match.group(2).strip().lower() == "disable":
                val = "normal"
            else:
                val = match.group(2).strip()
        except IndexError:
            val = "portfast"

        return {"stp": {"port_type": val}}

    def udld_port_Splus(self, data, match, int_obj):
        return {"udld": match.group(1)}

    def carrier_delay_dplus(self, data, match, int_obj):
        return {"udcarrier_delayld": match.group(1)}

    def no_optip_route_cache_optSplusopt(self, data, match, int_obj):
        if match.group(1):
            return {"ip": {"route_cache": False}}
        if match.group(2):
            val = match.group(2)
        else:
            val = True
        return {"ip": {"route_cache": val}}

    def ip_ospf_network_Splus(self, data, match, int_obj):
        return {"ospf": {"type": match.group(1)}}

    def ip_ospf_message_digest_key_dplus_Splus_Splus_Splus(self, data, match, int_obj):
        return [
            {"ospf": {"key": {match.group(1): {"type": match.group(2)}}}},
            {"ospf": {"key": {match.group(1): {"key_type": match.group(3)}}}},
            {"ospf": {"key": {match.group(1): {"key": match.group(4)}}}},
        ]

    def ip_vrf_forwarding_Splus(self, data, match, int_obj):
        return {"vrf": match.group(1)}

    def vrf_forwarding_Splus(self, data, match, int_obj):
        return self.ip_vrf_forwarding_Splus(data, match, int_obj)

    def vrf_member_Splus(self, data, match, int_obj):
        return self.ip_vrf_forwarding_Splus(data, match, int_obj)

    def vpc_dplus(self, data, match, int_obj):
        return {"vpc": match.group(1)}

    def no_optlacp_graceful_convergence(self, data, match, int_obj):
        if match.group(1):
            val = False
        else:
            val = True
        return {"lacp": {"graceful_convergence": val}}

    def no_optlacp_suspend_individual(self, data, match, int_obj):
        if match.group(1):
            val = False
        else:
            val = True
        return {"lacp": {"suspend_individual": val}}

    def vpc_peer_link(self, data, match, int_obj):
        return {"is_vpc_peerlink": True}


class portMigrationHelper(object):
    def __init__(self, data, target):
        self._log = logging.getLogger()
        self._cfg = CiscoConfParse(data.split("\n"))
        self._log.debug("successfully loaded configuration")
        self._data = collections.defaultdict(tree)
        self._regexCache = collections.defaultdict(tree)
        if target == "generic":
            self._tgt = TargetGeneric(self)
        else:
            self._log.error("target {0} not implemented".format(target))
            raise ValueError("target {0} not implemented".format(target))

    def getInterfaceName(self, interface):
        return " ".join(interface.text.split(" ")[-1:]).strip()

    def getRegex(self, rgx):
        if rgx not in self._regexCache:
            self._regexCache[rgx] = re.compile(rgx)
        return self._regexCache[rgx]

    def transformInterface(self, interfaces):
        for interface in interfaces:
            intName = self.getInterfaceName(interface)
            self._data[intName]["name"] = intName
            print("processing {0}".format(intName))
            for child in interface.re_search_children(r".*"):
                line = child.text.strip()
                found = False
                for regex in self._tgt.matrix:
                    match = self.getRegex(regex).match(line)
                    if match is not None:
                        found = True
                        retval = self._tgt.matrix[regex](line, match, interface)
                        if retval:
                            if isinstance(retval, type([])):
                                for item in retval:
                                    self._data[intName] = always_merger.merge(
                                        self._data[intName], item
                                    )
                            else:
                                self._data[intName] = always_merger.merge(
                                    self._data[intName], retval
                                )

                if not found:
                    raise Exception("Unknown config line '{0}'".format(line))

    def analyze_fex_hif_ports_cisco_nxos(self):
        self._FEXHostInterfaces = self._cfg.find_objects(
            r"^interface Ethernet\d+/\d+/\d+$"
        )
        self.transformInterface(self._FEXHostInterfaces)

    def analyze_physical_ports_cisco_nxos(self):
        self._PhysicalInterfaces = self._cfg.find_objects(
            r"^(interface Ethernet\d+/\d+)|(interface mgmt0)$"
        )
        self.transformInterface(self._PhysicalInterfaces)

    def analyze_physical_ports_cisco_ios(self):
        self._PhysicalInterfaces = self._cfg.find_objects(
            r"^interface \S+Ethernet\d+(/\d+)?(/\d+)?(/\d+)?$"
        )
        self.transformInterface(self._PhysicalInterfaces)

    def analyze_svi_cisco_ios(self):
        self._SVIs = self._cfg.find_objects(r"^interface Vlan\d+$")
        self.transformInterface(self._SVIs)

    def analyze_svi_cisco_nxos(self):
        self._SVIs = self._cfg.find_objects(r"^interface Vlan\d+$")
        self.transformInterface(self._SVIs)

    def analyze_fex_hif_ports_cisco_ios(self):
        self._log.warn("not supported")

    def analyze_port_channel_cisco_nxos(self):
        self._POs = self._cfg.find_objects(r"^interface [pP]ort-channel\d+\.?\d*$")
        self.transformInterface(self._POs)

    def analyze_port_channel_cisco_ios(self):
        self.analyze_port_channel_cisco_nxos()

        # self._data[intName]["isTrunk"]=self.isInterfaceTrunk(interface)
        # self._data[intName]["isAccess"]=self.isInterfaceAccess(interface)
        # self._data[intName]["isSwitchPort"]=self.isSwitchPort(interface)

        # self._SVInterfaces=self._cfg.find_objects(r"^interface Vlan")
        # self.transformInterface(self._SVInterfaces)
        # self._POInterfaces=self._cfg.find_objects(r"^interface port-channel")
        # self.transformInterface(self._POInterfaces)

    @property
    def data(self):
        return natsorted(self._data.items())


def port_migration_helper_process_data(
    data, ports, platform="cisco_nxos", target="generic"
):
    migrator = portMigrationHelper(data, target)
    try:
        fn = getattr(
            migrator,
            "analyze_{0}_{1}".format(ports.replace("-", "_").lower(), platform),
        )
    except AttributeError as e:
        migrator._log.error(
            "function {0} not implemented\n{1}".format(
                "analyze_{0}_{1}".format(ports.replace("-", "_").lower(), platform),
                e.message,
            )
        )
        return "[]"
    fn()
    return json.dumps(migrator.data, indent=2)


def expand_cisco_interface_name(shortname):
    if re.match(r"^Eth\d", shortname):
        return shortname.replace("Eth", "Ethernet")
    if re.match(r"^Po\d", shortname):
        return shortname.replace("Po", "port-channel")
    if re.match(r"^Gi\d", shortname):
        return shortname.replace("Gi", "GigabitEthernet")
    if re.match(r"^Te\d", shortname):
        return shortname.replace("Te", "TenGigabitEthernet")
    if re.match(r"^Fo\d", shortname):
        return shortname.replace("Fo", "FortyGigabitEthernet")
    if re.match(r"^Fa\d", shortname):
        return shortname.replace("Fa", "FastEthernet")

    return shortname


def calc_infra_rs_acc_base_grp_dn(switchname, port, card):
    log = logging.getLogger()
    if not card or card == 0:
        card = 1
    try:
        portname = "e1-{0:02d}".format(int(port))
    except ValueError:
        log.error("invalid port value: {0}".format(port))
        return ""
    if int(card) < 101:
        type = "accportprof"
    else:
        type = "fexprof"
    return "uni/infra/{0}-{1}/hports-{2}-typ-range/rsaccBaseGrp".format(
        type, switchname, portname
    )


def calc_infra_port_blk_dn(switchname, port, card):
    log = logging.getLogger()
    if not card or card == 0:
        card = 1
    try:
        portname = "e1-{0:02d}".format(int(port))
    except ValueError:
        log.error("invalid port value: {0}".format(port))
        return ""
    if int(card) < 101:
        type = "accportprof"
    else:
        type = "fexprof"

    return "uni/infra/{0}-{1}/hports-{2}-typ-range/portblk-block2".format(
        type, switchname, portname
    )


def get_lower_vpc_neighbour_from_name(switchname):
    match = re.compile(r"(\S+cs)(\d+)").match(switchname)
    swid = int(match.group(2))
    if swid % 2 == 1:
        return switchname
    else:
        return "{0}{1:04d}".format(match.group(1), swid - 1)


def calc_leaf_access_port_policy_group_name(switchname, port, type="single", db=None):
    log = logging.getLogger()
    log.debug("got switchname:{0} port:{1} type:{2}".format(switchname, port, type))
    try:
        portname = "e1-{0:02d}".format(int(port))
    except ValueError:
        log.error("invalid port value: {0}".format(port))
        return ""
    if type.lower() in ["vpc"]:
        match = re.compile(r"(\S+af)(\d+)-?(\d+)?").match(switchname)
        try:
            swid = int(match.group(2))
            sw_prefix = match.group(1)
        except AttributeError:
            log.error("invalid switchname value: {0}".format(switchname))
            return False
        fexid = False
        try:
            if match.group(3):
                fexid = "-{0}".format(match.group(3))
        except AttributeError:
            fexid = False
        if swid % 2 == 1:
            if fexid:
                return "{0}_{1}{3}-vpc-{2}".format(
                    switchname, swid + 1, 1000 + int(port), fexid
                )
            else:
                return "{0}_{1}-vpc-{2}".format(switchname, swid + 1, 1000 + int(port))
        else:
            if fexid:
                return "{0}{1}{4}_{2}{4}-vpc-{3}".format(
                    sw_prefix, swid - 1, swid, 1000 + int(port), fexid
                )
            else:
                return "{0}{1}_{2}-vpc-{3}".format(
                    sw_prefix, swid - 1, swid, 1000 + int(port)
                )
    elif type.lower() in ["po"]:
        return "{0}-po-{1}".format(switchname, 1000 + int(port))
    elif type.lower() in ["single"]:
        if switchname:
            return "{0}-{1}".format(switchname, portname)
        else:
            return False
    return False


def get_stp_mode_by_cfg(cfg, is_isl=False):
    if is_isl:
        return "STP-BPDU-Flood"
    return "STP-BPDU-Guard"


def get_cdp_mode_by_cfg(cfg, is_isl=False):
    if is_isl:
        return "CDP-Enabled"
    if cfg["cdp_enabled"]:
        return "CDP-Enabled"
    return "CDP-Disabled"


def get_lacp_mode_by_cfg(cfg):
    if cfg["lag_mode"].lower() == "static":
        return "LACP-Off"
    if cfg["lag_mode"].lower() == "lacp_active":
        return "LACP-Active"
    if cfg["lag_mode"].lower() == "lacp_passive":
        return "LACP-Passive"


def get_template_name_by_cfg(cfg, allcfg):
    log = logging.getLogger()
    if cfg["isL3"]:
        return "l3"
    if cfg["isMonitoring"]:
        log.error("monitoring ports not implemented")
        return ""
    if cfg["lacp_fast"]:
        log.warn("fast lacp ports not implemented")
        return ""
    if cfg["is_mlag_interface"] and cfg["lacp"]:
        pass
    if cfg["cdp_enabled"]:
        pass
