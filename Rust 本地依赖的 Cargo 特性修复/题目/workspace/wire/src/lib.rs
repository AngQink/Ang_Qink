#[cfg(all(feature="legacy", feature="modern"))]
compile_error!("wire features are exclusive");
#[cfg(not(any(feature="legacy",feature="modern")))]
compile_error!("select a wire profile");

#[cfg(feature="legacy")]
pub const ABI:i64=29;
#[cfg(feature="modern")]
pub const ABI:i64=43;
