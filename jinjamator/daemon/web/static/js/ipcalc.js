/*  Copyright 2010-2017 Thomas Rohmer-Kretz

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    http://trk.free.fr/ipcalc/

    JavaScript
*/

"use strict";

//==============================================
//   IP v4
//==============================================

/*--------------------------------------------
   ipIsValid
----------------------------------------------
 Returns true if an ip address is formatted exactly as it should be:
 no space, no extra zero, no incorrect value
 */
function ipIsValid(ip) {
    return ip === ipNbrToStr(ipStrToNbr(ip))
}

/*--------------------------------------------
   ipStrToNbr
----------------------------------------------
 Converts a text IP address to binary
 example:
   ipStrToNbr("1.2.3.4") returns 16909060
 */
function ipStrToNbr(ip) {
    return _ipToNbr(ip.split("."));
}

/*--------------------------------------------
   ipNbrToStr
----------------------------------------------
 Converts a binary IP address to text
 example:
   ipNbrToStr(16909060) returns "1.2.3.4"
 */
function ipNbrToStr(v) {
    return _ipFromNbr(v).join(".");
}

/*--------------------------------------------
   ipAdd
----------------------------------------------
 example:
   ipAdd("192.168.1.1"; 4) returns "192.168.1.5"
   ipAdd("192.168.1.1"; 256) returns "192.168.2.1"
 */
function ipAdd(ipStr, val) {
    return ipNbrToStr(ipStrToNbr(ipStr) + val);
}

/*--------------------------------------------
   ipDiff
----------------------------------------------
 difference between 2 IP addresses
 example:
   ipDiff("192.168.1.7"; "192.168.1.1") returns 6
 */
function ipDiff(ip1, ip2) {
    return ipStrToNbr(ip1) - ipStrToNbr(ip2);
}

/*--------------------------------------------
   ipAnd
----------------------------------------------
 bitwise AND
 example:
   ipAnd("192.168.1.1"; "255.255.255.0") returns "192.168.1.0"
 */
function ipAnd(ip1, ip2) {
    return _ipAnd(ip1.split("."), ip2.split(".")).join(".")
}

/*--------------------------------------------
   ipOr
----------------------------------------------
 bitwise OR
 example:
   ipOr("192.168.1.1"; "0.0.0.255") returns "192.168.1.255"
 */
function ipOr(ip1, ip2) {
    return _ipOr(ip1.split("."), ip2.split(".")).join(".")
}

/*--------------------------------------------
   ipXor
----------------------------------------------
 bitwise XOR
 example:
   ipXor("192.168.1.1"; "0.0.0.255") returns "192.168.1.254"
 */
function ipXor(ip1, ip2) {
    return _ipXor(ip1.split("."), ip2.split(".")).join(".")
}

/*--------------------------------------------
   ipGetByte
----------------------------------------------
 get one byte from an ip address given its position
 example:
   ipGetByte("192.168.1.1"; 1) returns 192
 */
function ipGetByte(ip, n) {
    ip = ip.split(".");
    return Number(ip[n - 1]);
}

/*--------------------------------------------
   ipSetByte
----------------------------------------------
 set one byte in an ip address given its position and value
 example:
   ipSetByte("192.168.1.1"; 4; 20) returns "192.168.1.20"
 */
function ipSetByte(ip, n, v) {
    ip = ip.split(".");
    ip[n - 1] = v;
    return ip.join(".")
}

/*--------------------------------------------
   ipMask
----------------------------------------------
 returns an IP netmask from a subnet
 both notations are accepted
 example:
   ipMask("192.168.1.1/24") returns "255.255.255.0"
   ipMask("192.168.1.1 255.255.255.0") returns "255.255.255.0"
 */
function ipMask(s) {
    return (new IpNet(s)).mask.join("."); 
}

/*--------------------------------------------
   ipWildMask
----------------------------------------------
 returns an IP Wildcard (inverse) mask from a subnet
 both notations are accepted
 example:
   ipWildMask("192.168.1.1/24") returns "0.0.0.255"
   ipWildMask("192.168.1.1 255.255.255.0") returns "0.0.0.255"
 */
function ipWildMask(s) {
    s = new IpNet(s);
    return ipNbrToStr(Math.pow(2, 32 - s.len) - 1);
}

/*--------------------------------------------
   ipInvertMask
----------------------------------------------
 returns an IP Wildcard (inverse) mask from a subnet mask
 or a subnet mask from a wildcard mask
 example:
   ipInvertMask("255.255.255.0") returns "0.0.0.255"
   ipInvertMask("0.0.0.255") returns "255.255.255.0"
 */
function ipInvertMask(ip) {
    return ipNbrToStr(Math.pow(2, 32) - 1 - ipStrToNbr(ip));
}

/*--------------------------------------------
   ipMaskLen
----------------------------------------------
 returns prefix length from a mask given by a string notation (xx.xx.xx.xx)
 example:
   ipMaskLen("255.255.255.0") returns 24 which is the number of bits of the subnetwork prefix
 */
function ipMaskLen(mask) {
    var bits = ipStrToNbr(mask).toString(2);
    return bits.lastIndexOf("1") + 1;
}

/*--------------------------------------------
   ipWithoutMask
----------------------------------------------
 removes the netmask notation at the end of the IP
 example:
   ipWithoutMask("192.168.1.1/24") returns "192.168.1.1"
   ipWithoutMask("192.168.1.1 255.255.255.0") returns "192.168.1.1"
 */
function ipWithoutMask(s) {
    return (new IpNet(s)).ip.join("."); 
}

/*--------------------------------------------
   ipSubnetLen
----------------------------------------------
 get the mask len from a subnet
 example:
   ipSubnetLen("192.168.1.1/24") returns 24
   ipSubnetLen("192.168.1.1 255.255.255.0") returns 24
 */
function ipSubnetLen(s) {
    return (new IpNet(s)).len; 
}

/*--------------------------------------------
   ipSubnetSize
----------------------------------------------
 returns the number of addresses in a subnet
 example:
   ipSubnetSize("192.168.1.32/29") returns 8
   ipSubnetSize("192.168.1.0 255.255.255.0") returns 256
 */
function ipSubnetSize(s) {
    return Math.pow(2, 32 - (new IpNet(s)).len);
}

/*--------------------------------------------
   ipClearHostBits
----------------------------------------------
 set to zero the bits in the host part of an address
 example:
   ipClearHostBits("192.168.1.1/24") returns "192.168.1.0/24"
   ipClearHostBits("192.168.1.193 255.255.255.128") returns "192.168.1.128 255.255.255.128"
 */
function ipClearHostBits(s) {
    return (new IpNet(s)).toString();
}

/*--------------------------------------------
   ipIsInSubnet
----------------------------------------------
 returns TRUE if "ip" is in "subnet"
 example:
   ipIsInSubnet("192.168.1.35"; "192.168.1.32/29") returns TRUE
   ipIsInSubnet("192.168.1.35"; "192.168.1.32 255.255.255.248") returns TRUE
   ipIsInSubnet("192.168.1.41"; "192.168.1.32/29") returns FALSE
 */
function ipIsInSubnet(ip, s) {
    return (new IpNet(s)).matchIp(ip.split(".")); 
}

/*--------------------------------------------
   ipSubnetIsInSubnet
----------------------------------------------
 returns TRUE if "subnet1" is in "subnet2"
 example:
   ipSubnetIsInSubnet("192.168.1.35/30"; "192.168.1.32/29") returns TRUE
   ipSubnetIsInSubnet("192.168.1.41/30"; "192.168.1.32/29") returns FALSE
   ipSubnetIsInSubnet("192.168.1.35/28"; "192.168.1.32/29") returns FALSE
 */
function ipSubnetIsInSubnet(s1, s2) {
    return (new IpNet(s2)).matchSubnet(new IpNet(s1)); 
}

/* only works with an ip
function ipSubnetMatch (ip, table) {
    var previousMatchLen = 0;
    var result = 0;
    var i;
    var rows = table.length;
    for (i = 0; i < rows; i++) {
        var s = new IpNet(Array.isArray(table[i]) ? table[i][0] : table[i]);
        if (s.matchIp(ip.split(".")) && (s.len > previousMatchLen)) {
            previousMatchLen = s.len;
            result = i + 1
        }
    }
    return result;
}
*/

/*--------------------------------------------
   ipSubnetMatch
----------------------------------------------
 tries to match an IP address or a subnet against a list of subnets in the
 left-most column of table_array and returns the row number
 this function selects the smallest matching subnet
 'ip' is the value to search for in the subnets in the first column of
      the table_array
 'table_array' is one or more columns of data
 returns 0 if the IP address is not matched.
 */
function ipSubnetMatch(ip, table) {
    var previousMatchLen = 0;
    var result = 0;
    var i;
    var rows = table.length;
    var s1 = new IpNet(ip);
    for (i = 0; i < rows; i++) {
        var s2 = new IpNet(Array.isArray(table[i]) ? table[i][0] : table[i]);
        if (s2.matchSubnet(s1) && (s2.len > previousMatchLen)) {
            previousMatchLen = s2.len;
            result = i + 1
        }
    }
    return result;
}

/*--------------------------------------------
   ipSubnetVLookup
----------------------------------------------
 tries to match an IP address or a subnet against a list of subnets in the
 left-most column of table_array and returns the value in the same row based
 on the index_number
 this function selects the smallest matching subnet
 'ip' is the value to search for in the subnets in the first column of
      the table_array
 'table_array' is one or more columns of data
 'index_number' is the column number in table_array from which the matching
      value must be returned. The first column which contains subnets is 1.
 note: add the subnet 0.0.0.0/0 at the end of the array if you want the
 function to return a default value
 */
 function ipSubnetVLookup(ip, table, index) {
    if (index === undefined) index = 1
    var row = ipSubnetMatch(ip, table);
    if (row) {
        return table[row - 1][index - 1];
    }
    return "Not Found";
}

/*--------------------------------------------
   ipSortArray
----------------------------------------------
 this function must be used in an array formula
 'ip_array' is a single column array containing ip addresses
 the return value is also a array of the same size containing the same
 addresses sorted in ascending or descending order
 'descending' is an optional parameter, if set to True the adresses are
 sorted in descending order
 */
function ipSortArray(arr, descending) {
    var desc = ((descending === undefined) || (descending == false)) ? 1 : -1;
    var sortFunc = Array.isArray(arr[0]) ?
        function(a, b) {return desc * ipDiff(a[0], b[0])} :
        function(a, b) {return desc * ipDiff(a, b)};
    arr.sort(sortFunc);
    return arr;
}

/*--------------------------------------------
   ipSubnetSortArray
----------------------------------------------
 this function must be used in an array formula
 'ip_array' is a single column array containing ip subnets or ip addresses
 the return value is also an array of the same size containing the same
 values sorted in ascending or descending order
 'descending' is an optional parameter, if set to True the subnets are
 sorted in descending order
 */
function ipSubnetSortArray(arr, descending) {
    var desc = ((descending === undefined) || (descending == false)) ? 1 : -1;
    var sortFunc = Array.isArray(arr[0]) ?
        function(a, b) {return desc * (new IpNet(a[0])).diff(new IpNet(b[0]))} :
        function(a, b) {return desc * (new IpNet(a)).diff(new IpNet(b))};
    arr.sort(sortFunc);
    return arr;
}

/*--------------------------------------------
   ipFindOverlappingSubnets
----------------------------------------------
 this function must be used in an array formula
 it will find in the list of subnets which subnets overlap
 'SubnetsArray' is a single column array containing a list of subnets, the
 list may be sorted or not
 the return value is also a array of the same size
 if the subnet on line x is included in a larger subnet from another line,
 this function returns an array in which line x contains the value of the
 larger subnet
 if the subnet on line x is distinct from any other subnet in the array,
 then this function returns on line x an empty cell
 if there are no overlapping subnets in the input array, the returned array
 is empty
 */
function ipFindOverlappingSubnets(arr) {
    var i, j;
    var size = arr.length;
    var nets = [];
    for (i = 0; i < size; i++) {
        nets.push(new IpNet(arr[i]));
    }
    var res = [];
    for (i = 0; i < size; i++) {
        res.push("");
        for (j = 0; j < size; j++) {
            if ((i != j) && nets[j].matchSubnet(nets[i])) {
                res[i] = arr[j];
                break;
            }
        }
    }
    return res;    
}

/*--------------------------------------------
   ipSubnetSortJoinArray
----------------------------------------------
 this fuction can sort and summarize subnets or ip routes
 it must be used in an array formula
 'ip_array' is a single column array containing ip subnets
 the return value is also an array of the same size containing the same
 subnets sorted in ascending order
 any consecutive subnets of the same size will be summarized when it is
 possible
 each line may contain any character sequence after the subnet, such as
 a next hop or any parameter of an ip route
 in this case, only subnets with the same parameters will be summarized
 */
function ipSubnetSortJoinArray(arr) {
    var i, j;
    var size = arr.length;
    var nets = [];
    var cidr = (arr[0].indexOf("/") >= 0);
    for (i = 0; i < size; i++) {
        nets.push(new IpNet(arr[i]));
    }
    nets.sort(function(a, b){return a.diff(b)});
    
    i = 0;
    while (i < nets.length - 1) {
        if (nets[i].nexthop == nets[i + 1].nexthop) {
            if (nets[i].matchSubnet(nets[i + 1])) {
                nets.splice(i + 1, 1);
                continue;
            }
            else if (nets[i + 1].matchSubnet(nets[i])) {
                nets.splice(i, 1);
                if (i > 0) i -= 1;
                continue;
            }
            else if (nets[i].len == nets[i + 1].len) {
                var bignet = new IpNet(nets[i].ip.join(".") + "/" + (nets[i].len - 1) + nets[i].nexthop);
                if (bignet.matchSubnet(nets[i + 1])) {
                    nets[i] = bignet;
                    nets.splice(i + 1, 1);
                    if (i > 0) i -= 1;
                    continue;
                }
            }
        }
        i += 1;
    }
    for (i = 0; i < nets.length; i++) nets[i] = nets[i].toString(cidr);
    return nets;
}

/*--------------------------------------------
   ipDivideSubnet
----------------------------------------------
 divide a network in smaller subnets
 "offset" is the value that will be added to the subnet length
   ipDivideSubnet("1.2.3.0/24"; 2) returns "1.2.3.0/26","1.2.3.64/26","1.2.3.128/26","1.2.3.192/26"
 */
function ipDivideSubnet(s, offset) {
    s = new IpNet(s);
    var len = s.len + Number(offset);
    if (len > 32) return "ERR subnet lenght > 32";
    s.setLen(len);
    var size = Math.pow(2, 32 - len);
    var v = _ipToNbr(s.ip);
    var n = Math.pow(2, offset);
    var nets = [];
    for (var i = 0; i < n; i++, v += size) {
        s.ip = _ipFromNbr(v);
        nets.push(s.toString());
    }
    return nets;
}

/*--------------------------------------------
   IpSubtractSubnets
----------------------------------------------
 remove subnets from a list of subnets
 this function must be used in an array formula
 'input_array' is a list of assigned subnets
 'subtract_array' is a list of used subnets
 the result is a list of unused subnets
 */
function ipSubtractSubnets(input_array, subtract_array) {
    var i;
    for (i = 0; i < subtract_array.length; i++) {
        // try to remove each network in subtract_array from the list in input_array
        var subtractNet = subtract_array[i];
        // try to remove each network in subtract_array from each network in input_array
        var j;
        for (j = 0; j < input_array.length;) {
            var net = input_array[j];
            // is the network to remove equal or larger ?
            if (ipSubnetIsInSubnet(net, subtractNet)) { // remove the network from input_array
                input_array.splice(j, 1);
            } 
            // is the network to remove smaller ?
            else if (ipSubnetIsInSubnet(subtractNet, net)) { // split this network in input_array
                var splitNets = ipDivideSubnet(net, 1);
                input_array.splice(j, 1, splitNets[0], splitNets[1]);
            } else {
                // nothing to do, skip to next network in input_array
                j = j + 1;
            }
        }
    }
    return input_array;
}

/*--------------------------------------------
   ipIsPrivate
----------------------------------------------
 returns TRUE if "ip" is in one of the private IP address ranges
 example:
   ipIsPrivate("192.168.1.35") returns TRUE
   ipIsPrivate("209.85.148.104") returns FALSE
 */
function ipIsPrivate(ip) {
    return ipIsInSubnet(ip, "10.0.0.0/8") || ipIsInSubnet(ip, "172.16.0.0/12") || ipIsInSubnet(ip, "192.168.0.0/16");
}

/*--------------------------------------------
   ipRangeToCIDR
----------------------------------------------
 returns a network or a list of networks given the first and the
 last address of an IP range
 example:
   IpRangeToCIDR("10.0.0.1","10.0.0.254") returns 10.0.0.0/24
   IpRangeToCIDR("10.0.0.1","10.0.1.63") returns the array 10.0.0.0/24 10.0.1.0/26
 note:
   10.0.0.0 or 10.0.0.1 as the first address returns the same result
   10.0.0.254 or 10.0.0.255 (broadcast) as the last address returns the same result
 */
function ipRangeToCIDR(firstAddr, lastAddr) {
    firstAddr = ipAnd(firstAddr, "255.255.255.254") // set the last bit to zero
    lastAddr = ipOr(lastAddr, "0.0.0.1") // set the last bit to one
    var l = 0
    do {// find the largest network which first address is firstAddr and which last address is not higher than lastAddr
        // build a network of length l
        // if it does not comply the above conditions, try with a smaller network
        l = l + 1
        var net = new IpNet(firstAddr + "/" + l);
        var ip1 = net.ip.join("."); // first @ of this network
        var ip2 = net.broadcast(); // last @ of this network
        var diff = ipDiff(ip2, lastAddr) // difference between the last @ of this network and the lastAddr we need to reach
    } while ((l < 32) && ((ip1 != firstAddr) || (diff > 0)))
    if (diff == 0) return [net.toString()];
    // if we haven't reached the lastAddr, recurse ipRangeToCIDR with firstAddr = the address following the network we found
    var tab = ipRangeToCIDR(ipAdd(ip2, 1), lastAddr);
    tab.unshift(net.toString());
    return tab;
}

/*--------------------------------------------
   internal functions to matipulate ip addresses as arrays
----------------------------------------------
*/
function _ipToNbr(ip) {
    var v = 0;
    for (var i = 0; i < ip.length; i++) {
        v = v * 256 + Number(ip[i]);
    }
    return v;
}

function _ipFromNbr(v) {
    var ip = [];
    while ((v > 0) || (ip.length < 4)) {
        ip.unshift(v % 256);
        v = Math.floor(v / 256);
    }
    return ip;
}

function _ipAnd(ip1, ip2) {
    var ip = [];
    for (var i = 0; i < 4; i++) {
        ip.push(Number(ip1[i]) & Number(ip2[i]));
    }
    return ip;
}

function _ipOr(ip1, ip2) {
    var ip = [];
    for (var i = 0; i < 4; i++) {
        ip.push(Number(ip1[i]) | Number(ip2[i]));
    }
    return ip;
}

function _ipXor(ip1, ip2) {
    var ip = [];
    for (var i = 0; i < 4; i++) {
        ip.push(Number(ip1[i]) ^ Number(ip2[i]));
    }
    return ip;
}

function _ipDiff(ip1, ip2) {
    return _ipToNbr(ip1) - _ipToNbr(ip2);
}

function _ipLenToMask(l) {
    return _ipFromNbr((Math.pow(2, l) - 1) * Math.pow(2, 32 - l))
}

function _ipLenToWildMask(l) {
    return _ipFromNbr(Math.pow(2, 32 - l) - 1)
}

function _ipMaskLen(mask) {
    var bits = _ipToNbr(mask).toString(2);
    return bits.lastIndexOf("1") + 1;
}

/*--------------------------------------------
   IpNet
----------------------------------------------
constructor for network object
 */
function IpNet(s) {
    var parse;
    this.cidr = true; // default notation
    if ((parse = /([\d\.]+)\/(\d+)(| .*)$/.exec(s)) != null) {
        this.ip = parse[1].split(".");
        this.len = Number(parse[2]);
        this.mask = _ipLenToMask(this.len);
        this.nexthop = parse[3];
        this.ip = _ipAnd(this.ip, this.mask);
    } else if ((parse = /([\d\.]+) ([\d\.]+)(| .*)$/.exec(s)) != null) {
        this.ip = parse[1].split(".");
        this.mask = parse[2].split(".");
        this.len = ipMaskLen(parse[2]);
        this.nexthop = parse[3];
        this.cidr = false;
        this.ip = _ipAnd(this.ip, this.mask);
    } else {
        this.ip = s.split(".");
        this.len = 32;
        this.nexthop = "";
        this.mask = [255, 255, 255, 255];
    }
    this.setLen = function (l) {
        this.len = l;
        this.mask = _ipLenToMask(l);
    };
    this.matchIp = function (ip2) {
        return this.ip.join(".") === _ipAnd(ip2, this.mask).join(".");
    };
    this.matchSubnet = function (s2) {
        return ((this.len <= s2.len) && (this.matchIp(s2.ip)))
    };
    this.diff = function (s2) {
        var d = _ipDiff(this.ip, s2.ip);
        if (d == 0) d = s2.len - this.len;
        return d;
    };
    this.toString = function (cidr) {
        if (cidr === undefined) cidr = this.cidr;
        return this.ip.join(".") + (cidr?"/"+this.len:" "+this.mask.join(".")) + this.nexthop;
    };
    this.broadcast = function () {
        return _ipOr(this.ip, _ipLenToWildMask(this.len)).join(".");
    };
}

/*--------------------------------------------
 */

//==============================================
//   IP v6
//==============================================

/*--------------------------------------------
   ipv6MaskLen
----------------------------------------------
 returns prefix length from an IPv6 net
 example:
   ipv6MaskLen("2001:db8:1f89::/48") returns 48
 */
function ipv6MaskLen(s) {
    return (new Ipv6(s)).len;
}

/*--------------------------------------------
   ipv6WithoutMask
----------------------------------------------
 removes the /xx netmask notation at the end of the IP
 example:
   ipv6WithoutMask("2001:db8:1f89::/48") returns "2001:db8:1f89::"
 */
function ipv6WithoutMask(s) {
    return s.split('/')[0];
}

/*--------------------------------------------
   ipv6IsInSubnet
----------------------------------------------
 returns TRUE if "ip" is in "subnet"
 example:
   ipv6IsInSubnet("2001:db8:1:::ac1f:1"; "2001:db8:1::/48") returns TRUE
   ipv6IsInSubnet("2001:db8:2:::ac1f:1"; "2001:db8:1::/48") returns FALSE
 */
function ipv6IsInSubnet(ip, s) {
    return (new Ipv6(s)).match(ip);
}

/*--------------------------------------------
   ipv6Expand
----------------------------------------------
 returns a representation of an IPv6 address with all the missing zeros
 the result has a fixed lenght of 39 caracters
 example :
   ipv6Expand("1:2:3::8") returns "0001:0002:0003:0000:0000:0000:0000:0008"
 */
function ipv6Expand(ip) {
    return (new Ipv6(ip)).long();
}

/*--------------------------------------------
   ipv6Compress
----------------------------------------------
 returns the shortest representation of an IPv6 address
 examples:
   ipv6Compress("0001:0002:0003:0000:0000:0000:0000:0008") returns "1:2:3::8"
   ipv6Compress("01:0:0::") returns "1::"
 */
function ipv6Compress(ip) {
    return (new Ipv6(ip)).compress();
}

/*--------------------------------------------
   ipv6ToBin
----------------------------------------------
 returns a string representing the binary value of IPv6 address
 the result has a fixed lenght of 128 characters
 */
function ipv6ToBin(ip) {
    return (new Ipv6(ip)).bin();
}

/*--------------------------------------------
   ipv6FromBin
----------------------------------------------
 returns an IPv6 from a string representing the binary value of IPv6 address
 the parameter must be a 128 character string
 */
function ipv6FromBin(b) {
    var ip = new Ipv6("");
    ip.fromBin(b);
    return ip.compress();
}

/*--------------------------------------------
   ipv6AddInt
----------------------------------------------
 Add a value to an IPv6 address
 example:
   ipv6AddInt("1::2"; 16) returns "1:12"
 */
function ipv6AddInt(ip, v) {
    var n = new Ipv6(ip);
    for (var i = 7; (v != 0) && (i >= 0); i--) {
        n.ar[i] += v;
        v = Math.floor(n.ar[i] / 0x10000);
        n.ar[i] -= v * 0x10000;
    }
    return n.compress();
}

/*--------------------------------------------
   ipv6Add
----------------------------------------------
 Add two IPv6 addresses
 example:
   ipv6Add("1:2::"; "::3") returns "1:2::3"
   ipv6Add("1:2::2"; "::3") returns "1:2::5"
 */
function ipv6Add(ip, ip2) {
    var n = new Ipv6(ip);
    var n2 = new Ipv6(ip2);
    var v = 0;
    for (var i = 7; i >= 0; i--) {
        n.ar[i] += n2.ar[i] + v;
        v = Math.floor(n.ar[i] / 0x10000);
        n.ar[i] -= v * 0x10000;
    }
    return n.compress();
}

/*--------------------------------------------
   ipv6GetBlock
----------------------------------------------
 Returns the 4-digit hexa block at position blockNbr
 The value of blockNbr can be 1 to 8, block 1 is the block on the left.
 example:
   ipv6GetBlock("2001:db8:1f89:c5a3::ac1f:8001"; 2) returns "0db8"
 */
function ipv6GetBlock(ip, pos) {
    return (new Ipv6(ip)).ar[pos - 1].toString(16);
}

/*--------------------------------------------
   ipv6GetBlockInt
----------------------------------------------
 Same as above except that the returned value is an integer between
 0 and 65535
 */
function ipv6GetBlockInt(ip, pos) {
    return (new Ipv6(ip)).ar[pos - 1];
}

/*--------------------------------------------
   ipv6SetBlock
----------------------------------------------
 Sets the value of the 4-digit hexa block at position blockNbr
 The value of blockNbr can be 1 to 8, block 1 is the block on the left.
 example:
   ipv6SetBlock("2001::"; 2; "db8") returns "2001:0db8::"
 */
function ipv6SetBlock(ip, pos, h) {
    var n = new Ipv6(ip);
    n.ar[pos - 1] = Number("0x0" + h) & 0xffff;
    return n.compress();
}

/*--------------------------------------------
   ipv6SetBlockInt
----------------------------------------------
 Same as above except that the block value is passed as an integer between
 0 and 65535
 */
function ipv6SetBlockInt(ip, pos, v) {
    var n = new Ipv6(ip);
    n.ar[pos - 1] = v & 0xffff;
    return n.compress();
}

/*--------------------------------------------
   ipv6SetBits
----------------------------------------------
 Sets on or more bits in a ip v6 addresse
 bits is a string with on or more "0" and "1"
 offset is the position of the first bit to set between 1 to 128 from left to right
 */
function ipv6SetBits(ip, pos, b) {
    var n = new Ipv6(ip);
    n.setBits(pos, b);
    return n.compress();
}

/*--------------------------------------------
   ipv6GetIpv4
----------------------------------------------
 Get the value of an IPv4 in an IPv6 at a given position
 exemple:
    ipv6GetIpv4("2001:c0a8:102::"; 2) returns "192.168.1.2"
 */
function ipv6GetIpv4(ipv6, blockNbr) {
    ipv6 = new Ipv6(ipv6);
    return ipNbrToStr(ipv6.ar[blockNbr-1] * 0x10000 + ipv6.ar[blockNbr]);
}

/*--------------------------------------------
   ipv6SetIpv4
----------------------------------------------
 Put the value of an IPv4 in an IPv6 at a given position
 exemple:
    ipv6SetIpv4("2001::"; 2; "192.168.1.2") returns "2001:c0a8:102::"
 */
function ipv6SetIpv4(ipv6, blockNbr, ipv4) {
    ipv6 = new Ipv6(ipv6);
    ipv4 = ipStrToNbr(ipv4);
    ipv6.ar[blockNbr-1] = Math.floor(ipv4 / 0x10000);
    ipv6.ar[blockNbr] = ipv4 - ipv6.ar[blockNbr-1] * 0x10000;
    return ipv6.compress();
}

/*--------------------------------------------
   ipv6SubnetFirstAddress
----------------------------------------------
 example:
   ipv6SubnetFirstAddress("2001:db8:1:1a0::/59") returns "2001:db8:1:1a0::"
 */
function ipv6SubnetFirstAddress(ip) {
    var n = new Ipv6(ip);
    n.setBits(n.len, "00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000".substr(0, 128 - n.len));
    return n.compress();
}

/*--------------------------------------------
   ipv6SubnetLastAddress
----------------------------------------------
 example:
   ipv6SubnetLastAddress("2001:db8:1:1a0::/59") returns "2001:db8:1:1bf:ffff:ffff:ffff:ffff"
 */
function ipv6SubnetLastAddress(ip) {
    var n = new Ipv6(ip);
    n.setBits(n.len, "11111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111".substr(0, 128 - n.len));
    return n.compress();
}

/*--------------------------------------------
   ipv6SortArray
----------------------------------------------
 this function must be used in an array formula
 'ip_array' is a single column array containing ip addresses
 the return value is also a array of the same size containing the same
 addresses sorted in ascending or descending order
 'descending' is an optional parameter, if set to True the adresses are
 sorted in descending order
 */
function ipv6SortArray(arr, descending) {
    var diff = function(a, b) {
        a = (new Ipv6(a)).long();
        b = (new Ipv6(b)).long();
        if (a == b) return 0;
        return (a < b) ? -1 : 1;
    };
    var desc = ((descending === undefined) || (descending == false)) ? 1 : -1;
    var sortFunc = Array.isArray(arr[0]) ?
        function(a, b) {return desc * diff(a[0], b[0])} :
        function(a, b) {return desc * diff(a, b)};
    arr.sort(sortFunc);
    return arr;
}

/*--------------------------------------------
   Ipv6
----------------------------------------------
constructor for IPv6 address or network
 */
function Ipv6(s) {
    s = s.split('/');
    this.len = Number(s[1]) || 128;
    if ((this.len < 0) || (this.len > 128)) this.len = 128;
    var t = s[0].split(':');
    if (t.length > 8) t.splice(8, t.length - 8);
    var dblcol = 0;
    for (var i = 0; i < t.length; i++) {
        if (t[i] == "") dblcol = i;
        t[i] = Number("0x0" + t[i]);
    }
    while (t.length < 8) t.splice(dblcol, 0, 0);
    this.ar = t;
    
    this.str = function() {
        var s = "";
        for (var i = 0; i < this.ar.length; i++)
            s = s + ":" + this.ar[i].toString(16);
        return s.substr(1);
    };
    
    this.compress = function() {
        var s = this.str();
        // try to replace the longuest sequence of zero blocks by ::
        var z = ":0:0:0:0:0:0:";
        while (z.length > 2) {
            var c = s.replace(z, "::");
            if (c != s) break;
            z = z.substr(2);
        }
        c = c.replace(/^0::/, "::");
        c = c.replace(/::0$/, "::");
        return c;
    }

    this.long = function() {
        var s = "";
        for (var i = 0; i < this.ar.length; i++)
            s = s + ":" + ("000" + this.ar[i].toString(16)).substr(-4);
        return s.substr(1);
    };

    this.bin = function() {
        var s = "";
        for (var i = 0; i < this.ar.length; i++)
            s = s + ("000000000000000" + this.ar[i].toString(2)).substr(-16);
        return s;
    };
    
    this.fromBin = function(s) {
        if (s.length != 128) return;
        for (var i = 0; i < this.ar.length; i++)
            this.ar[i] = parseInt(s.substr(i * 16, 16), 2);        
    };

    this.match = function(ip) {
        return this.bin().substr(0, this.len) == (new Ipv6(ip)).bin().substr(0, this.len);
    };

    this.setBits = function(pos, s) {
        var b = this.bin();
        this.fromBin(b.substr(0, pos) + s + b.substr(pos + s.length));
    };
}
