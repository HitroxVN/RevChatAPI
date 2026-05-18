const fs = require('fs');
const path = require('path');

// Giả lập các biến global của trình duyệt để xác thực WASM
global.Window = class { };
global.window = global;
global.self = global;

global.location = {
    get origin() {
        return 'https://www.easemate.ai';
    },
    get host() {
        return 'www.easemate.ai';
    },
    get hostname() {
        return 'www.easemate.ai';
    },
    get href() {
        return 'https://www.easemate.ai/webapp/chat?from=ai-chat';
    }
};

// Phân tích visitorId và identityId (tùy chọn) từ đối số CLI (process.argv[4] và process.argv[5])
const visitorId = process.argv[4] || "";
const identityId = process.argv[5] || "";

global.localStorage = {
    getItem: function (key) {
        if (key === 'app-main') {
            return JSON.stringify({
                visitorId: visitorId,
                identityId: identityId
            });
        }
        return null;
    }
};

(async () => {
    try {
        const wasmPath = path.join(__dirname, 'chat_generator.wasm');
        if (!fs.existsSync(wasmPath)) {
            console.error(`Không tìm thấy file WASM tại ${wasmPath}`);
            process.exit(1);
        }
        const buf = fs.readFileSync(wasmPath);

        let ve = null;
        let Er = null;
        let Va = null;
        let Ja = 0;
        const Ei = new TextEncoder();
        const zu = new TextDecoder('utf-8');

        function _o() {
            if (!Er || Er.buffer !== ve.memory.buffer) {
                Er = new Uint8Array(ve.memory.buffer);
            }
            return Er;
        }

        function fr() {
            if (!Va || Va.buffer !== ve.memory.buffer) {
                Va = new DataView(ve.memory.buffer);
            }
            return Va;
        }

        function Vr(e, t) {
            return zu.decode(_o().subarray(e, e + t));
        }

        function Qr(e, t, r) {
            if (r === void 0) {
                const s = Ei.encode(e),
                    u = t(s.length, 1) >>> 0;
                _o().subarray(u, u + s.length).set(s);
                Ja = s.length;
                return u;
            }
            let o = e.length,
                n = t(o, 1) >>> 0;
            const i = _o();
            let _ = 0;
            for (; _ < o; _++) {
                const s = e.charCodeAt(_);
                if (s > 127) break;
                i[n + _] = s;
            }
            if (_ !== o) {
                if (_ !== 0) {
                    e = e.slice(_);
                }
                n = r(n, o, o = _ + e.length * 3, 1) >>> 0;
                const s = _o().subarray(n + _, n + o),
                    u = Ei.encodeInto(e, s);
                _ += u.written || 0;
                n = r(n, o, _, 1) >>> 0;
            }
            Ja = _;
            return n;
        }

        function qa(e) {
            return e == null;
        }

        function vr(e) {
            const t = ve.__externref_table_alloc();
            ve.__wbindgen_export_2.set(t, e);
            return t;
        }

        function Mr(e, t) {
            try {
                return e.apply(null, t);
            } catch (r) {
                const o = vr(r);
                ve.__wbindgen_exn_store(o);
            }
        }

        const imports = {
            wbg: {
                __wbg_origin_00892013881c6e2b: function (...u) {
                    return Mr((m, c) => {
                        const d = c.origin;
                        const p = Qr(d, ve.__wbindgen_malloc, ve.__wbindgen_realloc),
                            l = Ja;
                        fr().setInt32(m + 4, l, !0);
                        fr().setInt32(m + 0, p, !0);
                    }, u);
                },
                __wbg_getItem_9fc74b31b896f95a: function (...u) {
                    return Mr((m, c, d, p) => {
                        const key = Vr(d, p);
                        const val = c.getItem(key);
                        const f = qa(val) ? 0 : Qr(val, ve.__wbindgen_malloc, ve.__wbindgen_realloc),
                            h = Ja;
                        fr().setInt32(m + 4, h, !0);
                        fr().setInt32(m + 0, f, !0);
                    }, u);
                },
                __wbg_instanceof_Window_12d20d558ef92592: function (u) {
                    return true;
                },
                __wbg_location_92d89c32ae076cab: function (u) {
                    return u.location;
                },
                __wbg_localStorage_9330af8bf39365ba: function (...u) {
                    return Mr(m => {
                        const c = m.localStorage;
                        return qa(c) ? 0 : vr(c);
                    }, u);
                },
                __wbg_newnoargs_254190557c45b4ec: function (u, m) {
                    const code = Vr(u, m);
                    return new Function(code);
                },
                __wbg_call_13410aac570ffff7: function (...u) {
                    return Mr((m, c) => m.call(c), u);
                },
                __wbg_stringify_b98c93d0a190446a: function (...u) {
                    return Mr(m => JSON.stringify(m), u);
                },
                __wbg_static_accessor_GLOBAL_THIS_f0a4409105898184: function () {
                    return globalThis;
                },
                __wbg_static_accessor_SELF_995b214ae681ff99: function () {
                    return self;
                },
                __wbg_static_accessor_WINDOW_cde3890479c675ea: function () {
                    return window;
                },
                __wbg_static_accessor_GLOBAL_8921f820c2ce3f12: function () {
                    return globalThis;
                },
                __wbg_wbindgenisnull_f3037694abe4d97a: function (u) {
                    return u === null;
                },
                __wbg_wbindgenisundefined_c4b71d073b92f3c5: function (u) {
                    return u === undefined;
                },
                __wbg_wbindgenisobject_307a53c6bd97fbf8: function (u) {
                    return typeof u === 'object' && u !== null;
                },
                __wbg_wbindgenisstring_d4fa939789f003b0: function (u) {
                    return typeof u === 'string';
                },
                __wbg_wbindgenstringget_0f16a6ddddef376f: function (u, m) {
                    const isStr = typeof m === 'string';
                    const d = isStr ? m : undefined;
                    let p = 0, l = 0;
                    if (d !== undefined) {
                        p = Qr(d, ve.__wbindgen_malloc, ve.__wbindgen_realloc);
                        l = Ja;
                    }
                    fr().setInt32(u + 4, l, !0);
                    fr().setInt32(u + 0, p, !0);
                },
                __wbg_wbindgenthrow_451ec1a8469d7eb6: function (u, m) {
                    const msg = Vr(u, m);
                    throw new Error(msg);
                },
                __wbindgen_init_externref_table: function () {
                    const u = ve.__wbindgen_export_2;
                    const m = u.grow(4);
                    u.set(0, void 0);
                    u.set(m + 0, void 0);
                    u.set(m + 1, null);
                    u.set(m + 2, !0);
                    u.set(m + 3, !1);
                }
            }
        };

        const { instance } = await WebAssembly.instantiate(buf, imports);
        ve = instance.exports;
        if (ve.__wbindgen_start) ve.__wbindgen_start();

        // Đọc body và timestamp (tùy chọn) từ đối số CLI
        const bodyStr = process.argv[2];
        let timestamp = process.argv[3];

        if (!timestamp) {
            // Tạo timestamp tính bằng nanoseconds
            const hrTime = process.hrtime();
            const epochNs = BigInt(Date.now()) * 1000000n + (BigInt(hrTime[1]) % 1000000n);
            timestamp = epochNs.toString();
        }

        const bodyObj = JSON.parse(bodyStr);

        const ptr = Qr(timestamp, ve.__wbindgen_malloc, ve.__wbindgen_realloc);
        const len = Ja;

        const resultPtrLen = ve.get_signs(bodyObj, ptr, len);
        const resString = Vr(resultPtrLen[0], resultPtrLen[1]);
        ve.__wbindgen_free(resultPtrLen[0], resultPtrLen[1], 1);

        console.log(resString);
    } catch (e) {
        console.error(e.stack);
        process.exit(1);
    }
})();
